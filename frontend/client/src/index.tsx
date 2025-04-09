import React from "react";
import ReactDOM from "react-dom/client";
import * as Sentry from '@sentry/react';
import { BrowserTracing } from '@sentry/tracing';
import { QueryClient, QueryClientProvider } from 'react-query';
import { RecoilRoot } from 'recoil';
import SupabaseProvider from '~shared/Providers/SupabaseProvider';
import ThemeProvider from '~shared/Providers/ThemeProvider';
import ApiErrorBoundaryProvider from '~shared/Providers/ApiErrorBoundaryProvider';
import App from './components/App';

import './styles/global.css';

Sentry.init({
  dsn: 'https://33edc136c49f638f27ba5912df6e0482@o4508916501970944.ingest.de.sentry.io/4509068742033488',
  integrations: [new BrowserTracing()],
  tracesSampleRate: 1.0,
  tracePropagationTargets: ["localhost", /\/api\//],
});

const queryClient = new QueryClient();

const root = ReactDOM.createRoot(document.getElementById("root")!);
root.render(
  <QueryClientProvider client={queryClient}>
    <RecoilRoot>
      <SupabaseProvider>
        <ThemeProvider>
          <ApiErrorBoundaryProvider>
            <App />
          </ApiErrorBoundaryProvider>
        </ThemeProvider>
      </SupabaseProvider>
    </RecoilRoot>
  </QueryClientProvider>
);
