/* eslint-disable import/prefer-default-export */
import { authenticated, api } from '.';

export const getProjectsList = () => authenticated(api).get('/projects/');

export const getProjectDetail = (id: string) =>
  authenticated(api).get(`/projects/${id}`);

export const postCreateProject = (data: any) =>
  authenticated(api).post('/projects', data, {
    headers: { 'Content-Type': 'application/json' },
  });

export const postPreviewSplitBySquare = (data: any) =>
  authenticated(api).post('/projects/preview-split-by-square/', data);

export const postTaskBoundary = ({ id, data }: { id: number; data: any }) =>
  authenticated(api).post(`/projects/${id}/upload-task-boundaries`, data);
