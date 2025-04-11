import React from 'react';

import { useAuthContext } from '~/hooks';

import Avatar from './Avatar';
import BackupCodesItem from './BackupCodesItem';
import DeleteAccount from './DeleteAccount';
import DisplayUsernameMessages from './DisplayUsernameMessages';
import EnableTwoFactorItem from './TwoFactorAuthentication';

function Account() {
  const user = useAuthContext();

  return (
    <div className="flex flex-col gap-3 p-1 text-sm text-text-primary">
      <div className="pb-3">
        <DisplayUsernameMessages />
      </div>
      <div className="pb-3">
        <Avatar />
      </div>
      {user?.user?.provider === 'local' && (
        <>
          <div className="pb-3">
            <EnableTwoFactorItem />
          </div>
          {user?.user?.twoFactorEnabled && (
            <div className="pb-3">
              <BackupCodesItem />
            </div>
          )}
        </>
      )}
      <div className="pb-3">
        <DeleteAccount />
      </div>
    </div>
  );
}

export default React.memo(Account);
