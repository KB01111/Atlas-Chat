import { Permissions, PermissionTypes } from "librechat-data-provider";
import type React from "react";
import { memo, useEffect, useMemo, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { useRecoilValue } from "recoil";
import rehypeHighlight from "rehype-highlight";
import rehypeKatex from "rehype-katex";
import remarkDirective from "remark-directive";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import supersub from "remark-supersub";
import type { Pluggable } from "unified";
import { Artifact, artifactPlugin } from "~/components/Artifacts/Artifact";
import CodeBlock from "~/components/Messages/Content/CodeBlock";
import { useFileDownload } from "~/data-provider";
import useHasAccess from "~/hooks/Roles/useHasAccess";
import useLocalize from "~/hooks/useLocalize";
import {
  ArtifactProvider,
  CodeBlockProvider,
  useCodeBlockContext,
  useToastContext,
} from "~/Providers";
import store from "~/store";
import { handleDoubleClick, langSubset, preprocessLaTeX } from "~/utils";

type TCodeProps = {
  inline?: boolean;
  className?: string;
  children: React.ReactNode;
};

export const code: React.ElementType = memo(
  ({ className, children }: TCodeProps) => {
    const canRunCode = useHasAccess({
      permissionType: PermissionTypes.RUN_CODE,
      permission: Permissions.USE,
    });
    const match = /language-(\w+)/.exec(className ?? "");
    const lang = match?.[1];
    const isMath = lang === "math";
    const isSingleLine =
      typeof children === "string" && children.split("\n").length === 1;

    const { getNextIndex, resetCounter } = useCodeBlockContext();
    const blockIndex = useRef(getNextIndex(isMath || isSingleLine)).current;

    useEffect(() => {
      resetCounter();
    }, [resetCounter]);

    if (isMath) {
      return <>{children}</>;
    }
    if (isSingleLine) {
      return (
        <code onDoubleClick={handleDoubleClick} className={className}>
          {children}
        </code>
      );
    }
    return (
      <CodeBlock
        lang={lang ?? "text"}
        codeChildren={children}
        blockIndex={blockIndex}
        allowExecution={canRunCode}
      />
    );
  },
);

export const codeNoExecution: React.ElementType = memo(
  ({ className, children }: TCodeProps) => {
    const match = /language-(\w+)/.exec(className ?? "");
    const lang = match?.[1];

    if (lang === "math") {
      return children;
    }
    if (typeof children === "string" && children.split("\n").length === 1) {
      return (
        <code onDoubleClick={handleDoubleClick} className={className}>
          {children}
        </code>
      );
    }
    return (
      <CodeBlock
        lang={lang ?? "text"}
        codeChildren={children}
        allowExecution={false}
      />
    );
  },
);

type TAnchorProps = {
  href: string;
  children: React.ReactNode;
};

export const a: React.ElementType = memo(({ href, children }: TAnchorProps) => {
  const user = useRecoilValue(store.user);
  const { showToast } = useToastContext();
  const localize = useLocalize();

  const {
    file_id = "",
    filename = "",
    filepath,
  } = useMemo(() => {
    const pattern = new RegExp(`(?:files|outputs)/${user?.id}/([^\\s]+)`);
    const match = href.match(pattern);
    if (match?.[0]) {
      const path = match[0];
      const parts = path.split("/");
      const name = parts.pop();
      const file_id = parts.pop();
      return { file_id, filename: name, filepath: path };
    }
    return { file_id: "", filename: "", filepath: "" };
  }, [user?.id, href]);

  const { refetch: downloadFile } = useFileDownload(user?.id ?? "", file_id);
  const props: { target?: string; onClick?: React.MouseEventHandler } = {
    target: "_new",
  };

  if (!file_id || !filename) {
    return (
      <a href={href} {...props}>
        {children}
      </a>
    );
  }

  const handleDownload = async (event: React.MouseEvent<HTMLAnchorElement>) => {
    event.preventDefault();
    try {
      const stream = await downloadFile();
      if (stream.data == null || stream.data === "") {
        console.error("Error downloading file: No data found");
        showToast({
          status: "error",
          message: localize("com_ui_download_error"),
        });
        return;
      }
      const link = document.createElement("a");
      link.href = stream.data;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(stream.data);
    } catch (error) {
      console.error("Error downloading file:", error);
    }
  };

  props.onClick = handleDownload;
  props.target = "_blank";

  return (
    <a
      href={
        filepath.startsWith("files/")
          ? `/api/${filepath}`
          : `/api/files/${filepath}`
      }
      {...props}
    >
      {children}
    </a>
  );
});

type TParagraphProps = {
  children: React.ReactNode;
};

export const p: React.ElementType = memo(({ children }: TParagraphProps) => {
  return <p className="mb-2 whitespace-pre-wrap">{children}</p>;
});

type TContentProps = {
  content: string;
  isLatestMessage: boolean;
};

const Markdown = memo(({ content = "", isLatestMessage }: TContentProps) => {
  const LaTeXParsing = useRecoilValue<boolean>(store.LaTeXParsing);
  const isInitializing = content === "";

  const currentContent = useMemo(() => {
    if (isInitializing) {
      return "";
    }
    return LaTeXParsing ? preprocessLaTeX(content) : content;
  }, [content, LaTeXParsing, isInitializing]);

  const rehypePlugins = useMemo(
    () => [
      [rehypeKatex, { output: "mathml" }],
      [
        rehypeHighlight,
        {
          detect: true,
          ignoreMissing: true,
          subset: langSubset,
        },
      ],
    ],
    [],
  );

  const remarkPlugins: Pluggable[] = useMemo(
    () => [
      supersub,
      remarkGfm,
      remarkDirective,
      artifactPlugin,
      [remarkMath, { singleDollarTextMath: true }],
    ],
    [],
  );

  if (isInitializing) {
    return (
      <div className="absolute">
        <p className="relative">
          <span className={isLatestMessage ? "result-thinking" : ""} />
        </p>
      </div>
    );
  }

  return (
    <ArtifactProvider>
      <CodeBlockProvider>
        <ReactMarkdown
          /** @ts-ignore */
          remarkPlugins={remarkPlugins}
          /* @ts-ignore */
          rehypePlugins={rehypePlugins}
          components={
            {
              code,
              a,
              p,
              artifact: Artifact,
            } as {
              [nodeType: string]: React.ElementType;
            }
          }
        >
          {currentContent}
        </ReactMarkdown>
      </CodeBlockProvider>
    </ArtifactProvider>
  );
});

export default Markdown;
