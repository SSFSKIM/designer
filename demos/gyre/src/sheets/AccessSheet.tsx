/**
 * Access: the one form on the page. Real labels, a real submit, an error that is
 * text next to the field rather than a red border alone, and a received state
 * that says what happens next.
 */

import { useId, useState, type ReactNode } from "react";

import { Sheet } from "./Sheet";

export function AccessSheet(props: { readonly onClose: () => void }): ReactNode {
  const emailId = useId();
  const orgId = useId();
  const errorId = useId();
  const [email, setEmail] = useState("");
  const [organisation, setOrganisation] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [received, setReceived] = useState(false);

  const submit = (event: { preventDefault(): void }): void => {
    event.preventDefault();
    const trimmed = email.trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) {
      setError("Enter an email address, for example mina.okafor@jamstec.jp.");
      return;
    }
    setError(null);
    setReceived(true);
  };

  return (
    <Sheet id="access" title="Request access" onClose={props.onClose}>
      {received ? (
        <div role="status">
          <p className="sheet__display">Request received.</p>
          <p>
            We reply within two working days with a workspace for {organisation.trim() || "your team"}
            {" "}and a note on which basins are resolved at 0.08° today.
          </p>
        </div>
      ) : (
        <form className="form" onSubmit={submit} noValidate>
          <p className="sheet__lead">
            Gyre is in a closed trial with research groups and route planners. Tell us where to
            send the workspace.
          </p>
          <div className="form__field">
            <label htmlFor={emailId}>Email</label>
            <input
              id={emailId}
              type="email"
              autoComplete="email"
              value={email}
              aria-invalid={error !== null}
              aria-describedby={error === null ? undefined : errorId}
              onChange={(event) => setEmail(event.target.value)}
            />
            {error === null ? null : (
              <p id={errorId} className="form__error">
                {error}
              </p>
            )}
          </div>
          <div className="form__field">
            <label htmlFor={orgId}>Organisation</label>
            <input
              id={orgId}
              type="text"
              autoComplete="organization"
              value={organisation}
              onChange={(event) => setOrganisation(event.target.value)}
            />
          </div>
          <button type="submit" className="button button--primary">
            Send request
          </button>
        </form>
      )}
    </Sheet>
  );
}
