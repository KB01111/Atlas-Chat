import type {
  TAttachment,
  TAttachmentMetadata,
  TFile,
} from "librechat-data-provider";
import { imageExtRegex } from "librechat-data-provider";
import Image from "~/components/Chat/Messages/Content/Image";

export default function Attachment({
  attachment,
}: {
  attachment?: TAttachment;
}) {
  if (!attachment) {
    return null;
  }
  const {
    width,
    height,
    filepath = null,
  } = attachment as TFile & TAttachmentMetadata;
  const isImage =
    imageExtRegex.test(attachment.filename) &&
    width != null &&
    height != null &&
    filepath != null;

  if (isImage) {
    return (
      <Image
        altText={attachment.filename}
        imagePath={filepath}
        height={height}
        width={width}
        className="mb-4"
      />
    );
  }
  return null;
}
