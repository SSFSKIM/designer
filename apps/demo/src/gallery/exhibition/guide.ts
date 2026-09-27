/**
 * The audio guide: the label read aloud by the browser's own speech synthesis.
 *
 * No audio files. A stop is the room's heading followed by the essay, split into sentences and
 * spoken one utterance at a time, which is what makes three things honest and simple: the
 * sentence being read can be marked in the essay, pause is "stop after remembering where", and
 * play resumes from that sentence (Chromium's `speechSynthesis.pause()` is unreliable across
 * platforms, and a guide that resumes from the sentence start is what a visitor expects anyway).
 *
 * Speech synthesis reports no duration before it speaks, so the one length shown before playing
 * is an estimate from word counts at an ordinary reading pace, and the transport says "about".
 * Once it plays, the transport shows what is known rather than an estimate: the real time spent
 * listening, and progress through the stop's text by character (the ring), which the
 * synthesiser's boundary events report as it goes.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import type { Work } from "./works";

/** Words per second at the synthesiser's default rate; used only to estimate lengths. */
const WORDS_PER_SECOND = 2.6;

export interface GuideStop {
  /** The heading, then the essay's sentences in order. */
  readonly sentences: readonly string[];
  /** For each essay paragraph, the indices into `sentences` it holds. */
  readonly paragraphs: readonly (readonly number[])[];
  /** Characters before each sentence, for progress by text. */
  readonly offsets: readonly number[];
  readonly totalCharacters: number;
  /** The estimated length, shown only before the stop has been played. */
  readonly estimatedSeconds: number;
}

/** Split a paragraph into sentences, keeping closing quotes with the sentence they end. */
export function splitSentences(paragraph: string): string[] {
  const parts = paragraph.match(/[^.!?]+(?:[.!?]+[”"’]?|$)/g) ?? [paragraph];
  const out: string[] = [];
  for (const part of parts) {
    const trimmed = part.trim();
    if (trimmed.length === 0) continue;
    // "c." and single initials are not sentence ends; glue a fragment that follows one.
    const previous = out[out.length - 1];
    if (previous !== undefined && /(?:\bc\.|\b[A-Z]\.)$/.test(previous)) {
      out[out.length - 1] = `${previous} ${trimmed}`;
    } else {
      out.push(trimmed);
    }
  }
  return out;
}

export function stopFor(work: Work): GuideStop {
  const heading = `${work.title}. ${work.artist}, ${work.date.replace("c.", "about")}.`;
  const sentences: string[] = [heading];
  const paragraphs: number[][] = [];
  for (const paragraph of work.essay) {
    const indices: number[] = [];
    for (const sentence of splitSentences(paragraph)) {
      indices.push(sentences.length);
      sentences.push(sentence);
    }
    paragraphs.push(indices);
  }
  const offsets: number[] = [];
  let total = 0;
  for (const sentence of sentences) {
    offsets.push(total);
    total += sentence.length;
  }
  const words = sentences.join(" ").split(/\s+/).filter(Boolean).length;
  return {
    sentences,
    paragraphs,
    offsets,
    totalCharacters: total,
    estimatedSeconds: words / WORDS_PER_SECOND + sentences.length * 0.35,
  };
}

export function formatSeconds(seconds: number): string {
  const whole = Math.max(0, Math.round(seconds));
  return `${Math.floor(whole / 60)}:${String(whole % 60).padStart(2, "0")}`;
}

export interface GuideState {
  readonly available: boolean;
  readonly playing: boolean;
  /** The sentence being read or next to be read. */
  readonly sentence: number;
  /** Real seconds spent playing this stop. */
  readonly elapsed: number;
  /** Progress through the stop's text, 0..1. */
  readonly progress: number;
  /** Nothing has been played yet, or the stop was started again. */
  readonly atStart: boolean;
  readonly stop: GuideStop;
  toggle(): void;
  reset(): void;
}

function pickVoice(): SpeechSynthesisVoice | undefined {
  const voices = window.speechSynthesis.getVoices();
  const english = voices.filter((voice) => voice.lang.toLowerCase().startsWith("en"));
  return (
    english.find((voice) => voice.localService && voice.default) ??
    english.find((voice) => voice.localService) ??
    english[0]
  );
}

export function useAudioGuide(work: Work): GuideState {
  const stop = useMemo(() => stopFor(work), [work]);
  const synth = typeof window !== "undefined" ? window.speechSynthesis : undefined;
  const [available, setAvailable] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [sentence, setSentence] = useState(0);
  const [within, setWithin] = useState(0);
  const [elapsed, setElapsed] = useState(0);
  const session = useRef(0);
  /** Milliseconds banked before the current run, and when the current run began. */
  const clock = useRef({ banked: 0, since: 0 });

  useEffect(() => {
    if (synth === undefined) return;
    const update = (): void => setAvailable(synth.getVoices().length > 0);
    update();
    synth.addEventListener("voiceschanged", update);
    return () => synth.removeEventListener("voiceschanged", update);
  }, [synth]);

  const halt = useCallback(
    (rewind: boolean) => {
      session.current += 1;
      synth?.cancel();
      if (clock.current.since > 0) {
        clock.current.banked += performance.now() - clock.current.since;
        clock.current.since = 0;
      }
      setPlaying(false);
      setWithin(0);
      if (rewind) {
        clock.current = { banked: 0, since: 0 };
        setSentence(0);
        setElapsed(0);
      } else {
        setElapsed(clock.current.banked / 1000);
      }
    },
    [synth],
  );

  // A new stop, or leaving the page, silences the guide and starts it over.
  useEffect(() => {
    halt(true);
    return () => {
      session.current += 1;
      synth?.cancel();
    };
  }, [halt, stop, synth]);

  // The listening clock, only while something is being read.
  useEffect(() => {
    if (!playing) return;
    const timer = window.setInterval(() => {
      const { banked, since } = clock.current;
      setElapsed((banked + (since > 0 ? performance.now() - since : 0)) / 1000);
    }, 250);
    return () => window.clearInterval(timer);
  }, [playing]);

  const speakFrom = useCallback(
    (index: number) => {
      if (synth === undefined) return;
      session.current += 1;
      const id = session.current;
      synth.cancel();
      const voice = pickVoice();
      const speak = (at: number): void => {
        if (id !== session.current) return;
        if (at >= stop.sentences.length) {
          halt(true);
          return;
        }
        const text = stop.sentences[at] ?? "";
        const utterance = new SpeechSynthesisUtterance(text);
        if (voice !== undefined) utterance.voice = voice;
        utterance.lang = voice?.lang ?? "en";
        utterance.onboundary = (event) => {
          if (id === session.current) setWithin(Math.min(1, event.charIndex / text.length));
        };
        utterance.onend = () => {
          if (id !== session.current) return;
          setWithin(0);
          setSentence(at + 1);
          speak(at + 1);
        };
        utterance.onerror = () => {
          if (id === session.current) halt(false);
        };
        setSentence(at);
        setWithin(0);
        synth.speak(utterance);
      };
      clock.current.since = performance.now();
      setPlaying(true);
      speak(index);
    },
    [halt, stop, synth],
  );

  const toggle = useCallback(() => {
    if (synth === undefined || !available) return;
    if (playing) halt(false);
    else speakFrom(sentence >= stop.sentences.length ? 0 : sentence);
  }, [available, halt, playing, sentence, speakFrom, stop.sentences.length, synth]);

  const reset = useCallback(() => halt(true), [halt]);

  const current = stop.sentences[sentence]?.length ?? 0;
  const progress =
    stop.totalCharacters > 0
      ? Math.min(1, ((stop.offsets[sentence] ?? stop.totalCharacters) + current * within) /
          stop.totalCharacters)
      : 0;
  const atStart = !playing && sentence === 0 && elapsed === 0;

  return { available, playing, sentence, elapsed, progress, atStart, stop, toggle, reset };
}
