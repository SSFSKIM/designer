import { chromium } from "@playwright/test";

// The established capture driver, with only the launch mode fixed for this gate.
const launch = chromium.launch.bind(chromium);
chromium.launch = (options) => launch({ ...options, headless: false });
await import("../../scripts/capture-web.ts");
