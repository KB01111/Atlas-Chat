import React from 'react';
import { useSupabase } from '../Providers/SupabaseProvider';

interface Props {
  children: React.ReactNode;
}

const PrivateRoute: React.FC<Props> = ({ children }) => {
  const { session } = useSupabase();

  if (!session) {
    return <div>Please log in to access this page.</div>;
  }

  return <>{children}</>;
};

export default PrivateRoute;
