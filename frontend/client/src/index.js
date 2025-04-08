import React from "react";
import ReactDOM from "react-dom/client";
import * as Sentry from '@sentry/react';
import { BrowserTracing } from '@sentry/tracing';

Sentry.init({
  dsn: 'https://33edc136c49f638f27ba5912df6e0482@o4508916501970944.ingest.de.sentry.io/4509068742033488',
  integrations: [new BrowserTracing()],
  tracesSampleRate: 1.0,
  tracePropagationTargets: ["localhost", /\/api\//],
});

const App = () => <div>Hello, Atlas Chat</div>;

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
