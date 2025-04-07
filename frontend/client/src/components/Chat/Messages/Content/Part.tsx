import type {
  TAttachment,
  TMessageContentParts,
} from "librechat-data-provider";
import {
  ContentTypes,
  imageGenTools,
  isImageVisionTool,
  ToolCallTypes,
  Tools,
} from "librechat-data-provider";
import { memo } from "react";
import CodeAnalyze from "./CodeAnalyze";
import Container from "./Container";
import Image from "./Image";
import ImageGen from "./ImageGen";
import { ErrorMessage } from "./MessageContent";
import AgentUpdate from "./Parts/AgentUpdate";
import EmptyText from "./Parts/EmptyText";
import ExecuteCode from "./Parts/ExecuteCode";
import Reasoning from "./Parts/Reasoning";
import Text from "./Parts/Text";
import RetrievalCall from "./RetrievalCall";
import ToolCall from "./ToolCall";

type PartProps = {
  part?: TMessageContentParts;
  isLast?: boolean;
  isSubmitting: boolean;
  showCursor: boolean;
  isCreatedByUser: boolean;
  attachments?: TAttachment[];
};

const Part = memo(
  ({
    part,
    isSubmitting,
    attachments,
    isLast,
    showCursor,
    isCreatedByUser,
  }: PartProps) => {
    if (!part) {
      return null;
    }

    if (part.type === ContentTypes.ERROR) {
      return (
        <ErrorMessage
          text={
            part[ContentTypes.ERROR] ??
            (typeof part[ContentTypes.TEXT] === "string"
              ? part[ContentTypes.TEXT]
              : part.text?.value) ??
            ""
          }
          className="my-2"
        />
      );
    }
    if (part.type === ContentTypes.AGENT_UPDATE) {
      return (
        <>
          <AgentUpdate
            currentAgentId={part[ContentTypes.AGENT_UPDATE]?.agentId}
          />
          {isLast && showCursor && (
            <Container>
              <EmptyText />
            </Container>
          )}
        </>
      );
    }
    if (part.type === ContentTypes.TEXT) {
      const text = typeof part.text === "string" ? part.text : part.text.value;

      if (typeof text !== "string") {
        return null;
      }
      if (part.tool_call_ids != null && !text) {
        return null;
      }
      return (
        <Container>
          <Text
            text={text}
            isCreatedByUser={isCreatedByUser}
            showCursor={showCursor}
          />
        </Container>
      );
    }
    if (part.type === ContentTypes.THINK) {
      const reasoning =
        typeof part.think === "string" ? part.think : part.think.value;
      if (typeof reasoning !== "string") {
        return null;
      }
      return <Reasoning reasoning={reasoning} />;
    }
    if (part.type === ContentTypes.TOOL_CALL) {
      const toolCall = part[ContentTypes.TOOL_CALL];

      if (!toolCall) {
        return null;
      }

      const isToolCall =
        "args" in toolCall &&
        (!toolCall.type || toolCall.type === ToolCallTypes.TOOL_CALL);
      if (isToolCall && toolCall.name === Tools.execute_code) {
        return (
          <ExecuteCode
            args={typeof toolCall.args === "string" ? toolCall.args : ""}
            output={toolCall.output ?? ""}
            initialProgress={toolCall.progress ?? 0.1}
            isSubmitting={isSubmitting}
            attachments={attachments}
          />
        );
      }
      if (isToolCall) {
        return (
          <ToolCall
            args={toolCall.args ?? ""}
            name={toolCall.name || ""}
            output={toolCall.output ?? ""}
            initialProgress={toolCall.progress ?? 0.1}
            isSubmitting={isSubmitting}
            attachments={attachments}
            auth={toolCall.auth}
            expires_at={toolCall.expires_at}
          />
        );
      }
      if (toolCall.type === ToolCallTypes.CODE_INTERPRETER) {
        const code_interpreter = toolCall[ToolCallTypes.CODE_INTERPRETER];
        return (
          <CodeAnalyze
            initialProgress={toolCall.progress ?? 0.1}
            code={code_interpreter.input}
            outputs={code_interpreter.outputs ?? []}
            isSubmitting={isSubmitting}
          />
        );
      }
      if (
        toolCall.type === ToolCallTypes.RETRIEVAL ||
        toolCall.type === ToolCallTypes.FILE_SEARCH
      ) {
        return (
          <RetrievalCall
            initialProgress={toolCall.progress ?? 0.1}
            isSubmitting={isSubmitting}
          />
        );
      }
      if (
        toolCall.type === ToolCallTypes.FUNCTION &&
        ToolCallTypes.FUNCTION in toolCall &&
        imageGenTools.has(toolCall.function.name)
      ) {
        return (
          <ImageGen
            initialProgress={toolCall.progress ?? 0.1}
            args={toolCall.function.arguments as string}
          />
        );
      }
      if (
        toolCall.type === ToolCallTypes.FUNCTION &&
        ToolCallTypes.FUNCTION in toolCall
      ) {
        if (isImageVisionTool(toolCall)) {
          if (isSubmitting && showCursor) {
            return (
              <Container>
                <Text
                  text={""}
                  isCreatedByUser={isCreatedByUser}
                  showCursor={showCursor}
                />
              </Container>
            );
          }
          return null;
        }

        return (
          <ToolCall
            initialProgress={toolCall.progress ?? 0.1}
            isSubmitting={isSubmitting}
            args={toolCall.function.arguments as string}
            name={toolCall.function.name}
            output={toolCall.function.output}
          />
        );
      }
    } else if (part.type === ContentTypes.IMAGE_FILE) {
      const imageFile = part[ContentTypes.IMAGE_FILE];
      const height = imageFile.height ?? 1920;
      const width = imageFile.width ?? 1080;
      return (
        <Image
          imagePath={imageFile.filepath}
          height={height}
          width={width}
          altText={imageFile.filename ?? "Uploaded Image"}
          placeholderDimensions={{
            height: `${height}px`,
            width: `${width}px`,
          }}
        />
      );
    }

    return null;
  },
);

export default Part;
