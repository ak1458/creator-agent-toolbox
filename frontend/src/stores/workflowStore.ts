import { create } from 'zustand'

interface WorkflowStoreState {
  selectedWorkflowId: string | null
  setSelectedWorkflowId: (workflowId: string | null) => void
}

export const useWorkflowStore = create<WorkflowStoreState>((set) => ({
  selectedWorkflowId: null,
  setSelectedWorkflowId: (workflowId) => set({ selectedWorkflowId: workflowId }),
}))
