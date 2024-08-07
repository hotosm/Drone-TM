/* eslint-disable consistent-return */
import { useCallback, useState } from 'react';
import { useTypedDispatch, useTypedSelector } from '@Store/hooks';
import { Controller } from 'react-hook-form';
import ErrorMessage from '@Components/common/FormUI/ErrorMessage';
import { UseFormPropsType } from '@Components/common/FormUI/types';
import { FormControl } from '@Components/common/FormUI';
import { Button } from '@Components/RadixComponents/Button';
import RadioButton from '@Components/common/RadioButton';
import { FlexColumn, FlexRow } from '@Components/common/Layouts';
import FileUpload from '@Components/common/UploadArea';
import {
  setCreateProjectState,
  resetUploadedAndDrawnAreas,
} from '@Store/actions/createproject';
import flatten from '@turf/flatten';
import area from '@turf/area';
import { FeatureCollection } from 'geojson';
import { uploadAreaOptions } from '@Constants/createProject';
import { validateGeoJSON } from '@Utils/convertLayerUtils';
import Icon from '@Components/common/Icon';
import { toast } from 'react-toastify';
import MapSection from './MapSection';

export default function DefineAOI({
  formProps,
}: {
  formProps: UseFormPropsType;
}) {
  const dispatch = useTypedDispatch();

  const { setValue, control, errors } = formProps;

  const [resetDrawTool, setResetDrawTool] = useState<null | (() => void)>(null);

  const projectArea = useTypedSelector(
    state => state.createproject.projectArea,
  );
  const noFlyZone = useTypedSelector(state => state.createproject.noFlyZone);
  const isNoflyzonePresent = useTypedSelector(
    state => state.createproject.isNoflyzonePresent,
  );
  const drawProjectAreaEnable = useTypedSelector(
    state => state.createproject.drawProjectAreaEnable,
  );
  const drawNoFlyZoneEnable = useTypedSelector(
    state => state.createproject.drawNoFlyZoneEnable,
  );
  const drawnProjectArea = useTypedSelector(
    state => state.createproject.drawnProjectArea,
  );
  const drawnNoFlyZone = useTypedSelector(
    state => state.createproject.drawnNoFlyZone,
  );

  const handleResetButtonClick = useCallback((resetFunction: any) => {
    setResetDrawTool(() => resetFunction);
  }, []);

  const handleDrawProjectAreaClick = () => {
    if (!drawProjectAreaEnable) {
      dispatch(setCreateProjectState({ drawProjectAreaEnable: true }));
      return;
    }
    const drawnArea =
      drawnProjectArea && area(drawnProjectArea as FeatureCollection);
    if (drawnArea && drawnArea > 100000000) {
      toast.error('Drawn Area should not exceed 100km²');
      dispatch(
        setCreateProjectState({
          drawProjectAreaEnable: false,
          drawnProjectArea: null,
        }),
      );
      // @ts-ignore
      resetDrawTool();
      return;
    }
    dispatch(
      setCreateProjectState({
        projectArea: drawnProjectArea,
        drawProjectAreaEnable: false,
      }),
    );
    setValue('outline', drawnProjectArea);
    if (resetDrawTool) {
      resetDrawTool();
    }
  };

  const handleDrawNoFlyZoneClick = () => {
    if (!drawNoFlyZoneEnable) {
      dispatch(setCreateProjectState({ drawNoFlyZoneEnable: true }));
      return;
    }
    if (!drawnNoFlyZone) return;
    const drawnNoFlyZoneArea =
      drawnProjectArea && area(drawnNoFlyZone as FeatureCollection);
    if (drawnNoFlyZoneArea && drawnNoFlyZoneArea > 100000000) {
      toast.error('Drawn Area should not exceed 100km²');
      dispatch(
        setCreateProjectState({
          drawNoFlyZoneEnable: false,
          drawnNoFlyZone: null,
        }),
      );
      // @ts-ignore
      resetDrawTool();
      return;
    }
    dispatch(
      setCreateProjectState({
        noFlyZone: drawnNoFlyZone,
        drawNoFlyZoneEnable: false,
      }),
    );
    setValue('no_fly_zones', drawnNoFlyZone);
    if (resetDrawTool) {
      resetDrawTool();
    }
  };

  const totalProjectArea =
    projectArea && area(projectArea as FeatureCollection);
  const noFlyZoneArea = noFlyZone && area(noFlyZone as FeatureCollection);

  const handleProjectAreaFileChange = (file: Record<string, any>[]) => {
    if (!file) return;
    const geojson: any = validateGeoJSON(file[0]?.file);

    try {
      geojson.then((z: any) => {
        if (typeof z === 'object' && !Array.isArray(z) && z !== null) {
          const convertedGeojson = flatten(z);
          dispatch(setCreateProjectState({ projectArea: convertedGeojson }));
          setValue('outline', convertedGeojson);
        }
      });
    } catch (err: any) {
      // eslint-disable-next-line no-console
      console.log(err);
    }
  };

  // @ts-ignore
  const validateAreaOfFileUpload = async (file: any) => {
    try {
      if (!file) return;
      const geojson: any = await validateGeoJSON(file[0]?.file);
      if (
        typeof geojson === 'object' &&
        !Array.isArray(geojson) &&
        geojson !== null
      ) {
        const convertedGeojson = flatten(geojson);
        const uploadedArea: any =
          convertedGeojson && area(convertedGeojson as FeatureCollection);
        if (uploadedArea && uploadedArea > 100000000) {
          toast.error('Drawn Area should not exceed 100km²');
          return false;
        }
        return true;
      }
      return false;
    } catch (err: any) {
      // eslint-disable-next-line no-console
      console.log(err);
      return false;
    }
  };

  const handleNoFlyZoneFileChange = (file: Record<string, any>[]) => {
    if (!file) return;
    const geojson = validateGeoJSON(file[0]?.file);
    try {
      geojson.then(z => {
        if (typeof z === 'object' && !Array.isArray(z) && z !== null) {
          const convertedGeojson = flatten(z);
          dispatch(setCreateProjectState({ noFlyZone: convertedGeojson }));
          setValue('no_fly_zones', convertedGeojson);
        }
      });
    } catch (err: any) {
      // eslint-disable-next-line no-console
      console.log(err);
    }
  };

  return (
    <FlexColumn>
      <div className="naxatw-bg-white">
        <div className="naxatw-grid naxatw-grid-cols-3">
          <div className="naxatw-col-span-1 naxatw-px-10 naxatw-py-5">
            <p className="naxatw-text-body-btn">
              Project Area <span className="naxatw-text-red">*</span>
            </p>
            {!projectArea ? (
              <>
                <FlexRow gap={3} className="naxatw-items-center">
                  <Button
                    className="naxatw-mt-2 naxatw-bg-red naxatw-text-white"
                    rightIcon={drawnProjectArea ? 'save' : 'draw'}
                    onClick={handleDrawProjectAreaClick}
                  >
                    {drawnProjectArea ? 'Save Drawn Area' : 'Draw Project Area'}
                  </Button>
                  {drawnProjectArea && (
                    <Icon
                      name="restart_alt"
                      className="naxatw-text-red"
                      onClick={() => {
                        dispatch(
                          setCreateProjectState({ drawnProjectArea: null }),
                        );
                        if (resetDrawTool) {
                          resetDrawTool();
                        }
                      }}
                    />
                  )}
                </FlexRow>
                {!drawProjectAreaEnable && (
                  <>
                    <FlexRow
                      className="naxatw-mt-1 naxatw-w-full naxatw-items-center naxatw-justify-center"
                      gap={3}
                    >
                      <hr className="naxatw-w-[40%]" />
                      <span>or</span>
                      <hr className="naxatw-w-[40%]" />
                    </FlexRow>
                    <FormControl className="naxatw-mt-2">
                      <Controller
                        control={control}
                        name="outline"
                        rules={{
                          required: 'Project Area is Required',
                        }}
                        render={({ field: { value } }) => {
                          // console.log(value, 'value12');
                          return (
                            <FileUpload
                              name="outline"
                              data={value}
                              onChange={handleProjectAreaFileChange}
                              fileAccept=".geojson, .kml"
                              placeholder="Upload project area (zipped shapefile, geojson or kml files)"
                              isValid={validateAreaOfFileUpload}
                              {...formProps}
                            />
                          );
                        }}
                      />
                      <ErrorMessage
                        message={errors?.outline?.message as string}
                      />
                    </FormControl>
                  </>
                )}
              </>
            ) : (
              <>
                <Button
                  variant="ghost"
                  className="naxatw-mt-2 naxatw-border naxatw-border-red naxatw-text-red"
                  rightIcon="restart_alt"
                  onClick={() => {
                    dispatch(resetUploadedAndDrawnAreas());
                  }}
                >
                  Reset Project Area
                </Button>
                <p className="naxatw-mt-2 naxatw-text-body-md">
                  Total Area: {Math.trunc(totalProjectArea as number)} m²
                </p>
                <div className="naxatw-mt-2">
                  <RadioButton
                    topic="No flying zone present in project area?"
                    options={uploadAreaOptions}
                    direction="column"
                    onChangeData={(val: 'yes' | 'no') => {
                      dispatch(
                        setCreateProjectState({ isNoflyzonePresent: val }),
                      );
                    }}
                    value={isNoflyzonePresent}
                  />
                </div>
                {isNoflyzonePresent === 'yes' && (
                  <div className="naxatw-mt-2">
                    {noFlyZone ? (
                      <>
                        <Button
                          variant="ghost"
                          className="naxatw-mb-2 naxatw-border naxatw-border-red naxatw-text-red"
                          rightIcon="restart_alt"
                          onClick={() =>
                            dispatch(
                              setCreateProjectState({
                                noFlyZone: null,
                                drawnNoFlyZone: null,
                                drawNoFlyZoneEnable: false,
                              }),
                            )
                          }
                        >
                          Reset No Fly Zone
                        </Button>
                        <p className="naxatw-mt-2 naxatw-text-body-md">
                          Total Area: {Math.trunc(noFlyZoneArea as number)} m2
                        </p>
                      </>
                    ) : (
                      <>
                        <FlexRow className="naxatw-items-center" gap={3}>
                          <Button
                            className="naxatw-mb-2 naxatw-bg-red naxatw-text-white"
                            rightIcon="draw"
                            onClick={handleDrawNoFlyZoneClick}
                          >
                            {!drawNoFlyZoneEnable
                              ? 'Draw No Fly Zone'
                              : 'Save No Fly Zone'}
                          </Button>
                          {drawnNoFlyZone && (
                            <Icon
                              name="restart_alt"
                              className="naxatw-text-red"
                              onClick={() => {
                                dispatch(
                                  setCreateProjectState({
                                    drawnNoFlyZone: null,
                                  }),
                                );
                                if (resetDrawTool) {
                                  resetDrawTool();
                                }
                              }}
                            />
                          )}
                        </FlexRow>
                        {!drawNoFlyZoneEnable && (
                          <>
                            <FlexRow
                              className="naxatw-my-1 naxatw-w-full naxatw-items-center naxatw-justify-center"
                              gap={3}
                            >
                              <hr className="naxatw-w-[40%]" />
                              <span>or</span>
                              <hr className="naxatw-w-[40%]" />
                            </FlexRow>
                            <FormControl className="naxatw-mt-2">
                              <Controller
                                control={control}
                                name="no_fly_zones"
                                render={({ field: { value } }) => (
                                  <FileUpload
                                    name="no_fly_zones"
                                    data={value}
                                    onChange={handleNoFlyZoneFileChange}
                                    isValid={validateAreaOfFileUpload}
                                    fileAccept=".geojson, .kml"
                                    placeholder="Upload project area (zipped shapefile, geojson or kml files)"
                                    {...formProps}
                                  />
                                )}
                              />
                            </FormControl>
                          </>
                        )}
                      </>
                    )}
                  </div>
                )}
              </>
            )}
          </div>
          <div className="naxatw-col-span-2 naxatw-overflow-hidden naxatw-rounded-md naxatw-border naxatw-border-[#F3C6C6]">
            <MapSection
              onResetButtonClick={handleResetButtonClick}
              handleDrawProjectAreaClick={handleDrawProjectAreaClick}
            />
          </div>
        </div>
      </div>
    </FlexColumn>
  );
}
