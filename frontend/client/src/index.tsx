import * as Sentry from '@sentry/react';
import { BrowserTracing } from '@sentry/tracing';
import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from 'react-query';
import { RecoilRoot } from 'recoil';

import ApiErrorBoundaryProvider from '~shared/Providers/ApiErrorBoundaryProvider';
import SupabaseProvider from '~shared/Providers/SupabaseProvider';
import ThemeProvider from '~shared/Providers/ThemeProvider';

import App from './components/App';

import './styles/global.css';

Sentry.init({
  dsn: process.env.REACT_APP_SENTRY_DSN,
  integrations: [new BrowserTracing()],
  tracesSampleRate: 1.0,
  environment: process.env.REACT_APP_SENTRY_ENVIRONMENT || 'development',
  tracePropagationTargets: ['localhost', /\/api\//],
});

// Trigger a test error to verify Sentry integration
Sentry.captureException(new Error('Sentry test error - integration verification'));

const queryClient = new QueryClient();

const root = ReactDOM.createRoot(document.getElementById('root')!);
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
  </QueryClientProvider>,
);
