import { useEffect } from 'react';
import { useRecoilState } from 'recoil';

import { useAuthContext } from '~/hooks/AuthContext';
import store from '~/store';

import StartupLayout from './Startup';

export default function LoginLayout() {
  const { isAuthenticated } = useAuthContext();
  const [queriesEnabled, setQueriesEnabled] = useRecoilState<boolean>(store.queriesEnabled);
  useEffect(() => {
    if (queriesEnabled) {
      return;
    }
    const timeout: NodeJS.Timeout = setTimeout(() => {
      setQueriesEnabled(true);
    }, 500);

    return () => {
      clearTimeout(timeout);
    };
  }, [queriesEnabled, setQueriesEnabled]);
  return <StartupLayout isAuthenticated={isAuthenticated} />;
}
