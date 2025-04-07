import { Anchor, Root } from "@radix-ui/react-popover";
import type { TInterfaceConfig, TPreset } from "librechat-data-provider";
import {
  EModelEndpoint,
  isParamEndpoint,
  tConvoUpdateSchema,
} from "librechat-data-provider";
import { useUserKeyQuery } from "librechat-data-provider/react-query";
import { Settings2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useRecoilState } from "recoil";
import { PluginStoreDialog, TooltipAnchor } from "~/components";
import {
  AlternativeSettings,
  EndpointSettings,
  SaveAsPresetDialog,
} from "~/components/Endpoints";
import { useGetEndpointsQuery } from "~/data-provider";
import { useLocalize, useMediaQuery, useSetIndexOptions } from "~/hooks";
import { useChatContext } from "~/Providers";
import store from "~/store";
import { getEndpointField } from "~/utils";
import OptionsPopover from "./OptionsPopover";
import PopoverButtons from "./PopoverButtons";

export default function HeaderOptions({
  interfaceConfig,
}: {
  interfaceConfig?: Partial<TInterfaceConfig>;
}) {
  const { data: endpointsConfig } = useGetEndpointsQuery();

  const [saveAsDialogShow, setSaveAsDialogShow] = useState<boolean>(false);
  const [showPluginStoreDialog, setShowPluginStoreDialog] = useRecoilState(
    store.showPluginStoreDialog,
  );
  const localize = useLocalize();

  const { showPopover, conversation, setShowPopover } = useChatContext();
  const { setOption } = useSetIndexOptions();
  const { endpoint, conversationId } = conversation ?? {};
  const { data: keyExpiry = { expiresAt: undefined } } = useUserKeyQuery(
    endpoint ?? "",
  );
  const userProvidesKey = useMemo(
    () => !!(endpointsConfig?.[endpoint ?? ""]?.userProvide ?? false),
    [endpointsConfig, endpoint],
  );
  const keyProvided = useMemo(
    () => (userProvidesKey ? !!(keyExpiry.expiresAt ?? "") : true),
    [keyExpiry.expiresAt, userProvidesKey],
  );

  const noSettings = useMemo<{ [key: string]: boolean }>(
    () => ({
      [EModelEndpoint.chatGPTBrowser]: true,
    }),
    [],
  );

  useEffect(() => {
    if (endpoint && noSettings[endpoint]) {
      setShowPopover(false);
    }
  }, [endpoint, noSettings, setShowPopover]);

  const saveAsPreset = () => {
    setSaveAsDialogShow(true);
  };

  if (!endpoint) {
    return null;
  }

  const triggerAdvancedMode = () => setShowPopover((prev) => !prev);

  const endpointType = getEndpointField(endpointsConfig, endpoint, "type");
  const paramEndpoint = isParamEndpoint(endpoint, endpointType);

  return (
    <Root
      open={showPopover}
      // onOpenChange={} //  called when the open state of the popover changes.
    >
      <Anchor>
        <div className="my-auto lg:max-w-2xl xl:max-w-3xl">
          <span className="flex w-full flex-col items-center justify-center gap-0 md:order-none md:m-auto md:gap-2">
            <div className="z-[61] flex w-full items-center justify-center gap-2">
              {!noSettings[endpoint] &&
                interfaceConfig?.parameters === true &&
                paramEndpoint === false && (
                  <TooltipAnchor
                    id="parameters-button"
                    aria-label={localize("com_ui_model_parameters")}
                    description={localize("com_ui_model_parameters")}
                    tabIndex={0}
                    role="button"
                    onClick={triggerAdvancedMode}
                    data-testid="parameters-button"
                    className="inline-flex size-10 items-center justify-center rounded-lg border border-border-light bg-transparent text-text-primary transition-all ease-in-out hover:bg-surface-tertiary disabled:pointer-events-none disabled:opacity-50 radix-state-open:bg-surface-tertiary"
                  >
                    <Settings2
                      size={16}
                      aria-label="Settings/Parameters Icon"
                    />
                  </TooltipAnchor>
                )}
            </div>
            {interfaceConfig?.parameters === true &&
              paramEndpoint === false && (
                <OptionsPopover
                  visible={showPopover}
                  saveAsPreset={saveAsPreset}
                  presetsDisabled={!(interfaceConfig.presets ?? false)}
                  PopoverButtons={<PopoverButtons />}
                  closePopover={() => setShowPopover(false)}
                >
                  <div className="px-4 py-4">
                    <EndpointSettings
                      className="[&::-webkit-scrollbar]:w-2"
                      conversation={conversation}
                      setOption={setOption}
                    />
                    <AlternativeSettings
                      conversation={conversation}
                      setOption={setOption}
                    />
                  </div>
                </OptionsPopover>
              )}
            {interfaceConfig?.presets === true && (
              <SaveAsPresetDialog
                open={saveAsDialogShow}
                onOpenChange={setSaveAsDialogShow}
                preset={
                  tConvoUpdateSchema.parse({
                    ...conversation,
                  }) as TPreset
                }
              />
            )}
            {interfaceConfig?.parameters === true && (
              <PluginStoreDialog
                isOpen={showPluginStoreDialog}
                setIsOpen={setShowPluginStoreDialog}
              />
            )}
          </span>
        </div>
      </Anchor>
    </Root>
  );
}
