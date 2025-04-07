import type { TEndpointsConfig, TModelSpec } from "librechat-data-provider";
import type React from "react";
import { memo } from "react";
import type { IconMapProps } from "~/common";
import { URLIcon } from "~/components/Endpoints/URLIcon";
import { icons } from "~/hooks/Endpoint/Icons";
import { getEndpointField, getIconKey, getModelSpecIconURL } from "~/utils";

interface SpecIconProps {
  currentSpec: TModelSpec;
  endpointsConfig: TEndpointsConfig;
}

type IconType = (props: IconMapProps) => React.JSX.Element;

const SpecIcon: React.FC<SpecIconProps> = ({
  currentSpec,
  endpointsConfig,
}) => {
  const iconURL = getModelSpecIconURL(currentSpec);
  const { endpoint } = currentSpec.preset;
  const endpointIconURL = getEndpointField(
    endpointsConfig,
    endpoint,
    "iconURL",
  );
  const iconKey = getIconKey({ endpoint, endpointsConfig, endpointIconURL });
  let Icon: IconType;

  if (!iconURL.includes("http")) {
    Icon = (icons[iconURL] ?? icons[iconKey] ?? icons.unknown) as IconType;
  } else if (iconURL) {
    return (
      <URLIcon
        iconURL={iconURL}
        altName={currentSpec.name}
        containerStyle={{ width: 20, height: 20 }}
        className="icon-md shrink-0 overflow-hidden rounded-full"
        endpoint={endpoint || undefined}
      />
    );
  } else {
    Icon = (icons[endpoint ?? ""] ??
      icons[iconKey] ??
      icons.unknown) as IconType;
  }

  return (
    <Icon
      size={20}
      endpoint={endpoint}
      context="menu-item"
      iconURL={endpointIconURL}
      className="icon-md shrink-0 text-text-primary"
    />
  );
};

export default memo(SpecIcon);
