import { UserProfileDetailsType } from '@Components/GoogleAuth';
import { api } from '.';

export const signInUser = (data: any) => api.post('/users/login/', data);

export const signInGoogle = () => api.get('/users/google-login');

export const signInCallBackUrl = () => api.get('/users/callback/');

export const logoutUser = () => api.post('/user/logout/');

export const postUserProfile = ({
  userId,
  userProfile,
}: {
  userId: number;
  userProfile: UserProfileDetailsType;
}) => api.post(`/users/${userId}/profile`, { data: userProfile });
