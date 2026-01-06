"use client";

import { useCoAgent, useCopilotAction } from "@copilotkit/react-core";
import { CopilotKitCSSProperties, CopilotSidebar } from "@copilotkit/react-ui";
import { useState } from "react";

export default function E3DevMindPage() {
  const [themeColor, setThemeColor] = useState("#10b981"); // E3 Green

  // Frontend action to change theme
  useCopilotAction({
    name: "setThemeColor",
    parameters: [{
      name: "themeColor",
      description: "The theme color to set.",
      required: true,
    }],
    handler({ themeColor }) {
      setThemeColor(themeColor);
    },
  });

  return (
    <main style={{ "--copilot-kit-primary-color": themeColor } as CopilotKitCSSProperties}>
      <E3DevMindContent themeColor={themeColor} />
      <CopilotSidebar
        clickOutsideToClose={false}
        defaultOpen={true}
        labels={{
          title: "E3 DevMind",
          initial: "Welcome to **E3 DevMind** - Your AI Development Assistant powered by CSDL-14B.\n\nI can help you with:\n- **Code Analysis**: \"Analyze the base_agent.py file\"\n- **Code Generation**: \"Generate a Python function for...\"\n- **Knowledge Search**: \"Search Archon for documentation on...\"\n- **Testing**: \"Run the tests for the agents module\"\n\nHow can I assist you today?"
        }}
      />
    </main>
  );
}

// E3 DevMind Agent State
type E3AgentState = {
  project_context: string;
  active_agents: string[];
  task_queue: { task: string; status: string }[];
}

function E3DevMindContent({ themeColor }: { themeColor: string }) {
  const {state, setState} = useCoAgent<E3AgentState>({
    name: "e3_devmind",
    initialState: {
      project_context: "E3 DevMind AI Development Platform",
      active_agents: [],
      task_queue: [],
    },
  });

  // Frontend action to add a task
  useCopilotAction({
    name: "addTask",
    parameters: [{
      name: "task",
      description: "Task description to add to the queue",
      required: true,
    }],
    handler: ({ task }) => {
      setState({
        ...state,
        task_queue: [...state.task_queue, { task, status: "pending" }],
      });
    },
  });

  // Frontend action for code analysis results
  useCopilotAction({
    name: "showCodeAnalysis",
    description: "Display code analysis results",
    available: "disabled",
    parameters: [
      { name: "filePath", type: "string", required: true },
      { name: "analysis", type: "string", required: false },
    ],
    render: ({ args }) => {
      return <CodeAnalysisCard filePath={args.filePath} themeColor={themeColor} />
    },
  });

  return (
    <div
      style={{ backgroundColor: themeColor }}
      className="h-screen w-screen flex justify-center items-center flex-col transition-colors duration-300"
    >
      <div className="bg-white/20 backdrop-blur-md p-8 rounded-2xl shadow-xl max-w-4xl w-full">
        <div className="flex items-center gap-4 mb-4">
          <div className="bg-white/30 p-3 rounded-xl">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <div>
            <h1 className="text-4xl font-bold text-white">E3 DevMind</h1>
            <p className="text-gray-200 italic">AI-Powered Development Assistant</p>
          </div>
        </div>

        <hr className="border-white/20 my-6" />

        {/* Project Context */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-white mb-2">Project Context</h2>
          <div className="bg-white/15 p-4 rounded-xl text-white">
            {state.project_context}
          </div>
        </div>

        {/* Active Agents */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-white mb-2">Active Agents</h2>
          <div className="flex flex-wrap gap-2">
            {state.active_agents?.length > 0 ? (
              state.active_agents.map((agent, index) => (
                <span key={index} className="bg-green-500/50 px-3 py-1 rounded-full text-white text-sm">
                  {agent}
                </span>
              ))
            ) : (
              <span className="text-white/60 italic">No active agents</span>
            )}
          </div>
        </div>

        {/* Task Queue */}
        <div>
          <h2 className="text-xl font-semibold text-white mb-2">Task Queue</h2>
          <div className="flex flex-col gap-2">
            {state.task_queue?.length > 0 ? (
              state.task_queue.map((item, index) => (
                <div
                  key={index}
                  className="bg-white/15 p-3 rounded-xl text-white flex justify-between items-center group hover:bg-white/20 transition-all"
                >
                  <span>{item.task}</span>
                  <span className={`text-sm px-2 py-1 rounded ${
                    item.status === 'completed' ? 'bg-green-500/50' :
                    item.status === 'in_progress' ? 'bg-yellow-500/50' : 'bg-gray-500/50'
                  }`}>
                    {item.status}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-white/60 italic">No tasks in queue. Ask me to help with something!</p>
            )}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-6 text-white/60 text-sm">
        Powered by CSDL-14B | AG-UI Protocol | CopilotKit
      </div>
    </div>
  );
}

// Code Analysis Card Component
function CodeAnalysisCard({ filePath, themeColor }: { filePath?: string, themeColor: string }) {
  return (
    <div
      style={{ backgroundColor: themeColor }}
      className="rounded-xl shadow-xl mt-6 mb-4 max-w-md w-full"
    >
      <div className="bg-white/20 p-4 w-full">
        <div className="flex items-center gap-3">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
          </svg>
          <div>
            <h3 className="text-lg font-bold text-white">Code Analysis</h3>
            <p className="text-white/80 text-sm truncate">{filePath}</p>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-white/20">
          <div className="grid grid-cols-2 gap-3 text-center">
            <div className="bg-white/10 p-2 rounded-lg">
              <p className="text-white text-xs">Lines</p>
              <p className="text-white font-medium">---</p>
            </div>
            <div className="bg-white/10 p-2 rounded-lg">
              <p className="text-white text-xs">Functions</p>
              <p className="text-white font-medium">---</p>
            </div>
            <div className="bg-white/10 p-2 rounded-lg">
              <p className="text-white text-xs">Classes</p>
              <p className="text-white font-medium">---</p>
            </div>
            <div className="bg-white/10 p-2 rounded-lg">
              <p className="text-white text-xs">Complexity</p>
              <p className="text-white font-medium">---</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
