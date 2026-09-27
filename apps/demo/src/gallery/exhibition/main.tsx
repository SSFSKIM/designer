/**
 * Exhibition gallery stub. The maker will build this page and its design record.
 */
import { GlassRoot, useGlassRootHandle } from "@vitreajs/vitrea-react";
import { StrictMode, useEffect, type ReactNode } from "react";
import { createRoot } from "react-dom/client";

function Placeholder(): ReactNode {
  const { root } = useGlassRootHandle();
  useEffect(() => {
    if (root === null) return;
    (window as unknown as Record<string, unknown>).__vitrea = root;
  }, [root]);
  return <p>This page is being built.</p>;
}

const container = document.getElementById("root");
if (container === null) throw new Error("The exhibition page has no #root to mount into.");

createRoot(container).render(
  <StrictMode>
    <GlassRoot renderer="webgpu" colorScheme="auto">
      <Placeholder />
    </GlassRoot>
  </StrictMode>,
);
