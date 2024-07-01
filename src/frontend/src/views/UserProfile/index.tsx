import { useTypedDispatch, useTypedSelector } from '@Store/hooks';
import { UserProfileHeader } from '@Components/UserProfile';
import { tabOptions } from '@Constants/index';
import { setCommonState } from '@Store/actions/common';
import { Button } from '@Components/RadixComponents/Button';
import {
  BasicDetails,
  OrganizationDetails,
  PasswordSection,
} from '@Components/UserProfile/FormContents';
import Tab from './UserProfileTabs';

const getActiveFormContent = (activeTab: number) => {
  switch (activeTab) {
    case 1:
      return <BasicDetails />;
    case 2:
      return <OrganizationDetails />;
    case 3:
      return <PasswordSection />;
    default:
      return <></>;
  }
};

export default function UserProfile() {
  const dispatch = useTypedDispatch();
  const userProfileActiveTab = useTypedSelector(
    state => state.common.userProfileActiveTab,
  );

  const onNextBtnClick = () => {
    if (userProfileActiveTab === 3) return;
    dispatch(
      setCommonState({ userProfileActiveTab: userProfileActiveTab + 1 }),
    );
  };

  return (
    <section className="naxatw-h-screen-nav naxatw-bg-grey-50 naxatw-px-16 naxatw-pt-8">
      <UserProfileHeader />
      <section className="naxatw-mt-5 naxatw-bg-grey-50 naxatw-px-80">
        <div className="naxatw-grid naxatw-h-[35rem] naxatw-grid-cols-3 naxatw-gap-14 naxatw-bg-white naxatw-py-10">
          <div className="naxatw-col-span-1">
            <Tab
              onTabChange={info => {
                dispatch(setCommonState({ userProfileActiveTab: info }));
              }}
              tabOptions={tabOptions}
              activeTab={userProfileActiveTab}
            />
          </div>
          <div className="naxatw-relative naxatw-col-span-2">
            {getActiveFormContent(userProfileActiveTab)}
            <Button
              className="naxatw-absolute naxatw-bottom-4 naxatw-right-4 naxatw-bg-red"
              rightIcon={
                userProfileActiveTab !== 3 ? 'chevron_right' : undefined
              }
              onClick={onNextBtnClick}
            >
              {userProfileActiveTab === 3 ? 'Complete Profile' : 'Next'}
            </Button>
          </div>
        </div>
      </section>
    </section>
  );
}
