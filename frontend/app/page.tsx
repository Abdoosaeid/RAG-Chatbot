"use client";

import React, { useState, useCallback } from "react";
import {
  useFrontendTool,
  useRenderTool,
  useAgentContext,
  useConfigureSuggestions,
  CopilotChat,
  useAgent,
  useCopilotKit,
} from "@copilotkit/react-core/v2";
import { z } from "zod";

const SUGGESTION_ACTIONS = [
  {
    title: "Change background",
    message: "Change the background to something new.",
    icon: "🎨",
  },
  {
    title: "Generate sonnet",
    message: "Write a short sonnet about AI.",
    icon: "✍️",
  },
  {
    title: "Get weather",
    message: "What's the weather in San Francisco?",
    icon: "🌤️",
  },
  {
    title: "Tell a joke",
    message: "Tell me a creative joke.",
    icon: "😄",
  },
] as const;

/* ── Custom welcome screen using children render function ──
   CopilotChat passes { welcomeMessage, input, suggestionView } to children.
   The `input` is the fully wired CopilotChat input (textarea + send + upload).
   We just lay it out beautifully in the centered hero. */
function CustomWelcomeScreen({ children }: any) {
  return (
    <div
      data-testid="copilot-welcome-screen"
      className="flex-1 flex flex-col items-center justify-center px-4 min-h-0"
    >
      <div className="w-full max-w-3xl flex flex-col items-center">
        {/* Logo + heading */}
        <div className="flex flex-col items-center gap-4 mb-8">
          <div className="flex items-center justify-center w-14 h-14 rounded-2xl bg-blue-600/15 shadow-lg shadow-blue-500/10">
            <svg
              width="26"
              height="26"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="text-blue-400"
            >
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight text-foreground text-center">
            How can I help you today?
          </h1>
          <p className="text-sm sm:text-base text-foreground/40 max-w-md text-center leading-relaxed">
            Ask me anything — from weather lookups to creative writing, I&apos;m here to assist.
          </p>
        </div>

        {/* The real CopilotChat input — passed via children render function */}
        <div className="w-full">
          {children &&
            children({
              /* We override the layout via children() but let
                 CopilotKit handle all input wiring internally */
            })}
        </div>
      </div>
    </div>
  );
}

/* ── Suggestion cards with send capability ── */
function SuggestionCards() {
  const { agent } = useAgent({ agentId: "sample_agent" });
  const { copilotkit } = useCopilotKit();

  const handleSend = useCallback(
    async (message: string) => {
      if (!agent || !copilotkit) return;
      agent.addMessage({
        id: crypto.randomUUID(),
        role: "user",
        content: message,
      });
      try {
        await copilotkit.runAgent({ agent });
      } catch (error) {
        console.error("SuggestionCards: runAgent failed", error);
      }
    },
    [agent, copilotkit],
  );

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg mt-6">
      {SUGGESTION_ACTIONS.map((action) => (
        <button
          key={action.title}
          onClick={() => handleSend(action.message)}
          type="button"
          className="group flex items-start gap-3 rounded-2xl border border-foreground/[0.07] bg-foreground/[0.03] hover:bg-foreground/[0.06] hover:border-foreground/[0.12] px-4 py-3.5 text-left transition-all duration-200 cursor-pointer backdrop-blur-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/50 focus-visible:ring-offset-2 focus-visible:ring-offset-background"
        >
          <span className="text-lg mt-0.5 shrink-0">{action.icon}</span>
          <div className="flex flex-col gap-0.5 min-w-0">
            <span className="text-sm font-medium text-foreground/80 group-hover:text-foreground/95 transition-colors">
              {action.title}
            </span>
            <span className="text-xs text-foreground/30 truncate">
              {action.message}
            </span>
          </div>
        </button>
      ))}
    </div>
  );
}

export default function Home() {
  const [background, setBackground] = useState<string>("--copilot-kit-background-color");

  useAgentContext({
    description: "Name of the user",
    value: "Bob",
  });

  useFrontendTool({
    name: "change_background",
    description:
      "Change the background color of the chat. Can be anything that the CSS background attribute accepts. Regular colors, linear of radial gradients etc.",
    parameters: z.object({
      background: z.string().describe("The background. Prefer gradients. Only use when asked."),
    }),
    handler: async ({ background }: { background: string }) => {
      setBackground(background);
      return {
        status: "success",
        message: `Background changed to ${background}`,
      };
    },
  });

  useRenderTool({
    name: "get_weather",
    parameters: z.object({
      location: z.string(),
    }),
    render: ({ args, result, status }: any) => {
      if (status !== "complete") {
        return <div data-testid="weather-info-loading">Loading weather...</div>;
      }

      let parsed: any = result;
      if (typeof parsed === "string") {
        try {
          parsed = JSON.parse(parsed);
        } catch {
          parsed = {};
        }
      }
      parsed = parsed ?? {};

      return (
        <div data-testid="weather-info">
          <strong>Weather in {parsed.city ?? args.location}</strong>
          <div>Temperature: {parsed.temperature}°C</div>
          <div>Humidity: {parsed.humidity}%</div>
          <div>Wind Speed: {parsed.windSpeed ?? parsed.wind_speed} mph</div>
          <div>Conditions: {parsed.conditions}</div>
        </div>
      );
    },
  });

  useConfigureSuggestions({
    suggestions: SUGGESTION_ACTIONS.map(({ title, message }) => ({ title, message })),
    available: "always",
  });

  return (
    <div
      data-testid="background-container"
      className="h-screen w-full"
      style={{ background }}
    >
      {/* CopilotChat owns the full viewport.
          - No messages → shows welcomeScreen (centered hero with real input)
          - Has messages → auto-switches to chat layout:
              scrollable messages (flex-1 overflow-y-auto)
              + pinned bottom input (absolute bottom-0 z-20)
          - PDF upload, drag-and-drop, multiline textarea all built-in. */}
      <CopilotChat
        agentId="sample_agent"
        className="h-full w-full max-w-4xl mx-auto"
        labels={{
          chatInputPlaceholder: "Message RAG Chatbot…",
          welcomeMessageText: "How can I help you today?",
        }}
        welcomeScreen={(slots: any) => (
          <div
            data-testid="copilot-welcome-screen"
            className="flex-1 flex flex-col items-center justify-center px-4"
          >
            <div className="w-full max-w-3xl flex flex-col items-center">
              {/* Logo + heading */}
              <div className="flex flex-col items-center gap-4 mb-8">
                <div className="flex items-center justify-center w-14 h-14 rounded-2xl bg-blue-600/15 shadow-lg shadow-blue-500/10">
                  <svg
                    width="26"
                    height="26"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="text-blue-400"
                  >
                    <path d="M12 2L2 7l10 5 10-5-10-5z" />
                    <path d="M2 17l10 5 10-5" />
                    <path d="M2 12l10 5 10-5" />
                  </svg>
                </div>
                <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight text-foreground text-center">
                  How can I help you today?
                </h1>
                <p className="text-sm sm:text-base text-foreground/40 max-w-md text-center leading-relaxed">
                  Ask me anything — from weather lookups to creative writing,
                  I&apos;m here to assist.
                </p>
              </div>

              {/* The real CopilotChat input — fully functional textarea + send + upload */}
              <div className="w-full">{slots.input}</div>

              {/* Clickable suggestion cards that send messages */}
              <SuggestionCards />

              {/* Fallback: CopilotKit's native suggestion pills */}
              <div className="mt-3">{slots.suggestionView}</div>
            </div>
          </div>
        )}
      />

      {/* Floating corner badge */}
      <div className="pointer-events-none fixed top-5 right-6 z-10">
        <span className="text-xs tracking-widest uppercase text-foreground/20 select-none">
          RAG Chatbot
        </span>
      </div>

      {/* Bottom disclaimer */}
      <div className="pointer-events-none fixed bottom-2 inset-x-0 z-10 text-center">
        <p className="text-[11px] text-foreground/15">
          RAG Chatbot can make mistakes. Consider checking important information.
        </p>
      </div>
    </div>
  );
}
