import React from 'react';
import ApiErrorBoundaryProvider from '~shared/Providers/ApiErrorBoundaryProvider';
import SupabaseProvider from '../Providers/SupabaseProvider';
import ThemeProvider from '../Providers/ThemeProvider';

const App: React.FC = () => {
  return (
    <ApiErrorBoundaryProvider>
      <SupabaseProvider>
        <ThemeProvider>
          <div>
            <h1>Atlas Chat</h1>
            <p>Welcome to Atlas Chat frontend scaffold.</p>
          </div>
        </ThemeProvider>
      </SupabaseProvider>
    </ApiErrorBoundaryProvider>
  );
};

export default App;
