import { createSlice } from '@reduxjs/toolkit';
import type { CaseReducer, PayloadAction } from '@reduxjs/toolkit';
import {
  ModalContentsType,
  PromptDialogContentsType,
} from '@Constants/modalContents';
import persist from '@Store/persist';

export interface CommonState {
  showModal: boolean;
  modalContent: ModalContentsType;
  showPromptDialog: boolean;
  promptDialogContent: PromptDialogContentsType;
  showMap: boolean;
  userProfileActiveTab: number;
}

const initialState: CommonState = {
  showModal: false,
  modalContent: null,
  showPromptDialog: false,
  promptDialogContent: null,
  showMap: false,
  userProfileActiveTab: 1,
};

const setCommonState: CaseReducer<
  CommonState,
  PayloadAction<Partial<CommonState>>
> = (state, action) => ({
  ...state,
  ...action.payload,
});

const toggleModal: CaseReducer<
  CommonState,
  PayloadAction<ModalContentsType | undefined>
> = (state, action) => ({
  ...state,
  showModal: !!action.payload,
  modalContent: action.payload || state.modalContent,
});

const setModalContent: CaseReducer<
  CommonState,
  PayloadAction<ModalContentsType>
> = (state, action) => ({
  ...state,
  modalContent: action.payload || null,
});

const togglePromptDialog: CaseReducer<
  CommonState,
  PayloadAction<PromptDialogContentsType | undefined>
> = (state, action) => ({
  ...state,
  showPromptDialog: !!action.payload || !state.showPromptDialog,
  promptDialogContent: action.payload || state.promptDialogContent,
});

const setPromptDialogContent: CaseReducer<
  CommonState,
  PayloadAction<PromptDialogContentsType>
> = (state, action) => ({
  ...state,
  promptDialogContent: action.payload || null,
});

const commonSlice = createSlice({
  name: 'common',
  initialState,
  reducers: {
    setCommonState,
    toggleModal,
    setModalContent,
    togglePromptDialog,
    setPromptDialogContent,
  },
});

export { commonSlice };

export default persist('common', [], commonSlice.reducer);
