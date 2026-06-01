import { create } from 'zustand';

const useRealtimeStore = create((set) => ({
  events: [],
  connectionStatus: 'disconnected',

  addEvent: (event) =>
    set((s) => ({ events: [event, ...s.events].slice(0, 100) })),

  setConnectionStatus: (status) => set({ connectionStatus: status }),

  clearEvents: () => set({ events: [] }),
}));

export default useRealtimeStore;
