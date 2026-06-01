import { create } from 'zustand';

const useCopilotStore = create((set) => ({
  messages: [],
  isStreaming: false,
  activeAgent: null,

  addMessage: (msg) =>
    set((s) => ({ messages: [...s.messages, { id: Date.now(), timestamp: new Date(), ...msg }] })),

  updateLastMessage: (content) =>
    set((s) => {
      const msgs = [...s.messages];
      if (msgs.length > 0) msgs[msgs.length - 1].content = content;
      return { messages: msgs };
    }),

  setStreaming: (val) => set({ isStreaming: val }),
  setActiveAgent: (agent) => set({ activeAgent: agent }),
  clearMessages: () => set({ messages: [] }),
}));

export default useCopilotStore;
