import { NextRequest } from "next/server";
import {
  CopilotRuntime,
  copilotRuntimeNextJSAppRouterEndpoint,
  ExperimentalEmptyAdapter,
  copilotKitEndpoint,
} from "@copilotkit/runtime";
import { LangGraphHttpAgent } from "@copilotkit/runtime/langgraph";

const serviceAdapter = new ExperimentalEmptyAdapter();

// E3 DevMind AG-UI Server URL
const AGUI_URL = process.env.E3_AGUI_URL || "http://localhost:8100";

// Create agent that points to our AG-UI server
const e3DevMindAgent = new LangGraphHttpAgent({
  name: "e3_devmind",
  description: "E3 DevMind - AI-powered development assistant using CSDL-14B",
  url: AGUI_URL,
});

const runtime = new CopilotRuntime({
  remoteEndpoints: [
    copilotKitEndpoint({
      url: AGUI_URL,
    }),
  ],
  agents: {
    e3_devmind: e3DevMindAgent,
  },
});

export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit",
  });

  return handleRequest(req);
};

// GET handler for agent discovery
export const GET = async () => {
  // Fetch agent info from the AG-UI server
  try {
    const aguiInfo = await fetch(`${AGUI_URL}/info`);
    const aguiData = await aguiInfo.json();

    return new Response(JSON.stringify({
      version: "1.50.1",
      agents: aguiData.agents?.reduce((acc: Record<string, any>, agent: any) => {
        acc[agent.name] = {
          name: agent.name,
          description: agent.description,
        };
        return acc;
      }, {}) || {},
      audioFileTranscriptionEnabled: false,
    }), {
      headers: { "Content-Type": "application/json" },
    });
  } catch {
    return new Response(JSON.stringify({
      version: "1.50.1",
      agents: {
        e3_devmind: {
          name: "e3_devmind",
          description: "E3 DevMind - AI-powered development assistant using CSDL-14B",
        },
      },
      audioFileTranscriptionEnabled: false,
    }), {
      headers: { "Content-Type": "application/json" },
    });
  }
};
