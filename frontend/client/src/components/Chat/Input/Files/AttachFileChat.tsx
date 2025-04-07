import {
  fileConfig as defaultFileConfig,
  type EndpointFileConfig,
  isAgentsEndpoint,
  mergeFileConfig,
  supportsFiles,
} from "librechat-data-provider";
import { memo, useMemo } from "react";
import { useRecoilValue } from "recoil";
import { useGetFileConfig } from "~/data-provider";
import { useChatContext } from "~/Providers";
import store from "~/store";
import AttachFile from "./AttachFile";
import AttachFileMenu from "./AttachFileMenu";

function AttachFileChat({ disableInputs }: { disableInputs: boolean }) {
  const { conversation } = useChatContext();

  const { endpoint: _endpoint, endpointType } = conversation ?? {
    endpoint: null,
  };

  const isAgents = useMemo(() => isAgentsEndpoint(_endpoint), [_endpoint]);

  const { data: fileConfig = defaultFileConfig } = useGetFileConfig({
    select: (data) => mergeFileConfig(data),
  });

  const endpointFileConfig = fileConfig.endpoints[_endpoint ?? ""] as
    | EndpointFileConfig
    | undefined;

  const endpointSupportsFiles: boolean =
    supportsFiles[endpointType ?? _endpoint ?? ""] ?? false;
  const isUploadDisabled =
    (disableInputs || endpointFileConfig?.disabled) ?? false;

  if (isAgents) {
    return <AttachFileMenu disabled={disableInputs} />;
  }
  if (endpointSupportsFiles && !isUploadDisabled) {
    return <AttachFile disabled={disableInputs} />;
  }

  return null;
}

export default memo(AttachFileChat);
