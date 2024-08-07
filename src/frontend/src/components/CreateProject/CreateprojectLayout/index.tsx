import { useNavigate } from 'react-router-dom';
import { useTypedSelector, useTypedDispatch } from '@Store/hooks';
import { useMutation } from '@tanstack/react-query';
import { FieldValues, useForm } from 'react-hook-form';
import {
  BasicInformationForm,
  DefineAOIForm,
  KeyParametersForm,
  ContributionsForm,
  GenerateTaskForm,
} from '@Components/CreateProject/FormContents';
import { UseFormPropsType } from '@Components/common/FormUI/types';
import { FlexRow } from '@Components/common/Layouts';
import { Button } from '@Components/RadixComponents/Button';
import {
  resetUploadedAndDrawnAreas,
  setCreateProjectState,
} from '@Store/actions/createproject';
import { postCreateProject, postTaskBoundary } from '@Services/createproject';
import { toast } from 'react-toastify';
import {
  StepComponentMap,
  stepDescriptionComponents,
} from '@Constants/createProject';
import { convertGeojsonToFile } from '@Utils/convertLayerUtils';
import prepareFormData from '@Utils/prepareFormData';

/**
 * This function looks up the provided map of components to find and return
 * the component associated with the current active step. If no component
 * is found for the given step, it returns an empty fragment.
 *
 * @param {StepComponentMap} componentsMap - An object mapping step numbers to React functional components.
 * @param {number} activeStep - The current active step number.
 * @returns {JSX.Element} - The React component for the active step, or an empty fragment if not found.
 */
const getActiveStepDescription = (
  componentsMap: StepComponentMap,
  activeStep: number,
): JSX.Element => {
  const Component = componentsMap[activeStep];
  return Component ? <Component /> : <></>;
};

const getActiveStepForm = (activeStep: number, formProps: UseFormPropsType) => {
  switch (activeStep) {
    case 1:
      return <BasicInformationForm formProps={formProps} />;
    case 2:
      return <DefineAOIForm formProps={formProps} />;
    case 3:
      return <KeyParametersForm formProps={formProps} />;
    case 4:
      return <GenerateTaskForm formProps={formProps} />;
    case 5:
      return <ContributionsForm formProps={formProps} />;
    default:
      return <></>;
  }
};

export default function CreateprojectLayout() {
  const dispatch = useTypedDispatch();
  const navigate = useNavigate();

  const activeStep = useTypedSelector(state => state.createproject.activeStep);
  const splitGeojson = useTypedSelector(
    state => state.createproject.splitGeojson,
  );
  const isTerrainFollow = useTypedSelector(
    state => state.createproject.isTerrainFollow,
  );
  const isNoflyzonePresent = useTypedSelector(
    state => state.createproject.isNoflyzonePresent,
  );

  const initialState: FieldValues = {
    name: '',
    short_description: '',
    description: '',
    outline: null,
    no_fly_zones: null,
    gsd_cm_px: null,
    dimension: null,
    is_terrain_follow: null,
    task_split_type: 1,
    per_task_instructions: '',
    deadline_at: '',
    visibility: 0,
  };

  const {
    register,
    setValue,
    handleSubmit,
    reset,
    formState: { errors },
    control,
    getValues,
    watch,
  } = useForm({
    defaultValues: initialState,
  });

  const { mutate: uploadTaskBoundary, isLoading } = useMutation<
    any,
    any,
    any,
    unknown
  >({
    mutationFn: postTaskBoundary,
    onSuccess: () => {
      toast.success('Project Created Successfully');
      reset();
      dispatch(
        setCreateProjectState({
          activeStep: 1,
          splitGeojson: null,
          uploadedProjectArea: null,
          uploadedNoFlyZone: null,
        }),
      );
      navigate('/projects');
    },
    onError: err => {
      toast.error(err.message);
    },
  });

  const { mutate: createProject } = useMutation<any, any, any, unknown>({
    mutationFn: postCreateProject,
    onSuccess: (res: any) => {
      dispatch(setCreateProjectState({ projectId: res.data.project_id }));
      if (!splitGeojson) return;
      const geojson = convertGeojsonToFile(splitGeojson);
      const formData = prepareFormData({ task_geojson: geojson });
      uploadTaskBoundary({ id: res.data.project_id, data: formData });
      reset();
      dispatch(resetUploadedAndDrawnAreas());
    },
    onError: err => {
      toast.error(err.message);
    },
  });

  const formProps = {
    register,
    setValue,
    reset,
    errors,
    control,
    getValues,
    watch,
  };

  const onPrevBtnClick = () => {
    dispatch(setCreateProjectState({ activeStep: activeStep - 1 }));
  };

  const onSubmit = (data: any) => {
    if (activeStep === 2) {
      if (
        !data?.outline ||
        (Array.isArray(data?.outline) &&
          data?.outline?.length === 0)
      ) {
        toast.error('Please upload or draw and save project area');
        return;
      }
      if (
        isNoflyzonePresent === 'yes' &&
        (!data?.no_fly_zones ||
          data?.no_fly_zones?.length === 0)
      ) {
        toast.error('Please upload or draw and save No Fly zone area');
        return;
      }
    }

    if (activeStep === 4 && !splitGeojson) return;
    if (activeStep !== 5) {
      dispatch(setCreateProjectState({ activeStep: activeStep + 1 }));
      return;
    }
    const payload = {
      ...data,
      is_terrain_follow: isTerrainFollow === 'hilly',
    };
    // remove key
    if (isNoflyzonePresent === 'no') delete payload?.no_fly_zones;

    createProject(payload);
  };

  return (
    <section className="project-form-layout naxatw-bg-[#FAFAFA]">
      <div className="naxatw-grid naxatw-grid-cols-4 naxatw-gap-5">
        {/* description */}
        <div className="description naxatw-col-span-1 naxatw-h-[32.625rem] naxatw-animate-fade-up naxatw-bg-white">
          {getActiveStepDescription(stepDescriptionComponents, activeStep)}
        </div>

        {/* form section */}
        <div className="form naxatw-relative naxatw-col-span-3 naxatw-bg-white">
          {getActiveStepForm(activeStep, formProps)}
          <FlexRow className="naxatw-absolute naxatw-bottom-5 naxatw-w-full naxatw-justify-between naxatw-px-10">
            {activeStep !== 1 ? (
              <Button
                onClick={onPrevBtnClick}
                className="!naxatw-text-red"
                leftIcon="chevron_left"
              >
                Previous
              </Button>
            ) : (
              <div />
            )}
            <Button
              onClick={e => {
                e.preventDefault();
                handleSubmit(onSubmit)();
              }}
              type="submit"
              className="!naxatw-bg-red !naxatw-text-white"
              rightIcon="chevron_right"
              withLoader
              isLoading={isLoading}
            >
              {activeStep === 5 ? 'Save' : 'Next'}
            </Button>
          </FlexRow>
        </div>
      </div>
    </section>
  );
}
