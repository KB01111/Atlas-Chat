import { memo } from "react";
import { useRecoilValue } from "recoil";
import { useFileHandling } from "~/hooks";
import { useChatContext } from "~/Providers";
import store from "~/store";
import FileRow from "./FileRow";

function FileFormChat({ disableInputs }: { disableInputs: boolean }) {
  const chatDirection = useRecoilValue(store.chatDirection).toLowerCase();
  const { files, setFiles, conversation, setFilesLoading } = useChatContext();
  const { endpoint: _endpoint } = conversation ?? { endpoint: null };
  const { abortUpload } = useFileHandling();

  const isRTL = chatDirection === "rtl";

  return (
    <>
      <FileRow
        files={files}
        setFiles={setFiles}
        abortUpload={abortUpload}
        setFilesLoading={setFilesLoading}
        isRTL={isRTL}
        Wrapper={({ children }) => (
          <div className="mx-2 mt-2 flex flex-wrap gap-2">{children}</div>
        )}
      />
    </>
  );
}

export default memo(FileFormChat);
