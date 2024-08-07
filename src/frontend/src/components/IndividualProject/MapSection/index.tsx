/* eslint-disable no-nested-ternary */
/* eslint-disable no-unused-vars */
import { useParams } from 'react-router-dom';
import { useCallback, useEffect, useState } from 'react';
import { useTypedSelector, useTypedDispatch } from '@Store/hooks';
import { useMapLibreGLMap } from '@Components/common/MapLibreComponents';
import VectorLayer from '@Components/common/MapLibreComponents/Layers/VectorLayer';
import MapContainer from '@Components/common/MapLibreComponents/MapContainer';
import BaseLayerSwitcher from '@Components/common/MapLibreComponents/BaseLayerSwitcher';
import { GeojsonType } from '@Components/common/MapLibreComponents/types';
import AsyncPopup from '@Components/common/MapLibreComponents/AsyncPopup';
import getBbox from '@turf/bbox';
import { FeatureCollection } from 'geojson';
import { LngLatBoundsLike, Map } from 'maplibre-gl';
import { setProjectState } from '@Store/actions/project';
import { useGetTaskStatesQuery } from '@Api/projects';
import DTMLogo from '@Assets/images/lock.png';
import { postTaskStatus } from '@Services/project';
import { useMutation } from '@tanstack/react-query';
import { toast } from 'react-toastify';

export default function MapSection() {
  const { id } = useParams();
  const dispatch = useTypedDispatch();
  const [taskStatusObj, setTaskStatusObj] = useState<Record<
    string,
    any
  > | null>(null);

  const { map, isMapLoaded } = useMapLibreGLMap({
    mapOptions: {
      zoom: 5,
      center: [84.124, 28.3949],
      maxZoom: 19,
    },
    disableRotation: true,
  });

  const selectedTaskId = useTypedSelector(
    state => state.project.selectedTaskId,
  );
  const tasksData = useTypedSelector(state => state.project.tasksData);

  const { data: taskStates } = useGetTaskStatesQuery(id as string, {
    enabled: !!tasksData,
  });

  const { mutate: lockTask } = useMutation<any, any, any, unknown>({
    mutationFn: postTaskStatus,
    onSuccess: (res: any) => {
      toast.success('Task Requested for Mapping');
      setTaskStatusObj({
        ...taskStatusObj,
        [res.data.task_id]: 'REQUEST_FOR_MAPPING',
      });
    },
    onError: (err: any) => {
      toast.error(err.message);
    },
  });

  useEffect(() => {
    if (!map || !taskStates) return;
    // @ts-ignore
    const taskStatus: Record<string, any> = taskStates?.reduce(
      (acc: Record<string, any>, task: Record<string, any>) => {
        acc[task.task_id] = task.state;
        return acc;
      },
      {},
    );
    setTaskStatusObj(taskStatus);
  }, [map, taskStates]);

  // zoom to layer in the project area
  useEffect(() => {
    if (!tasksData) return;
    const tasksCollectiveGeojson = tasksData?.reduce(
      (acc, curr) => {
        return {
          ...acc,
          features: [...acc.features, curr.outline],
        };
      },
      {
        type: 'FeatureCollection',
        features: [],
      },
    );
    const bbox = getBbox(tasksCollectiveGeojson as FeatureCollection);
    map?.fitBounds(bbox as LngLatBoundsLike, { padding: 25 });
  }, [map, tasksData]);

  const getPopupUI = useCallback(
    (properties: Record<string, any>) => {
      const status = taskStatusObj?.[properties?.id];
      const popupText = (taskStatus: string) => {
        switch (taskStatus) {
          case 'UNLOCKED_TO_MAP':
            return 'This task is available for mapping';
          case 'REQUEST_FOR_MAPPING':
            return 'This task is Requested for mapping';
          case 'LOCKED_FOR_MAPPING':
            return 'This task is locked for mapping';
          default:
            return 'This Task is completed';
        }
      };
      return <h6>{popupText(status)}</h6>;
    },
    [taskStatusObj],
  );

  const handleTaskLockClick = () => {
    lockTask({
      projectId: id,
      taskId: selectedTaskId,
      data: { event: 'request' },
    });
  };

  return (
    <MapContainer
      map={map}
      isMapLoaded={isMapLoaded}
      style={{
        width: '100%',
        height: '100%',
      }}
    >
      {tasksData &&
        tasksData?.map((task: Record<string, any>) => {
          return (
            <VectorLayer
              key={task?.id}
              map={map as Map}
              id={`tasks-layer-${task?.id}-${taskStatusObj?.[task?.id]}`}
              visibleOnMap={task?.id && taskStatusObj}
              geojson={task.outline as GeojsonType}
              interactions={['feature']}
              layerOptions={
                taskStatusObj?.[`${task?.id}`] === 'LOCKED_FOR_MAPPING'
                  ? {
                      type: 'fill',
                      paint: {
                        'fill-color': '#98BBC8',
                        'fill-outline-color': '#484848',
                        'fill-opacity': 0.6,
                      },
                    }
                  : taskStatusObj?.[`${task?.id}`] === 'REQUEST_FOR_MAPPING'
                    ? {
                        type: 'fill',
                        paint: {
                          'fill-color': '#F3C5C5',
                          'fill-outline-color': '#484848',
                          'fill-opacity': 0.7,
                        },
                      }
                    : taskStatusObj?.[`${task?.id}`] === 'UNLOCKED_TO_VALIDATE'
                      ? {
                          type: 'fill',
                          paint: {
                            'fill-color': '#176149',
                            'fill-outline-color': '#484848',
                            'fill-opacity': 0.5,
                          },
                        }
                      : {
                          type: 'fill',
                          paint: {
                            'fill-color': '#ffffff',
                            'fill-outline-color': '#484848',
                            'fill-opacity': 0.4,
                          },
                        }
              }
              hasImage={
                taskStatusObj?.[`${task?.id}`] === 'LOCKED_FOR_MAPPING' || false
              }
              image={DTMLogo}
            />
          );
        })}

      <AsyncPopup
        map={map as Map}
        popupUI={getPopupUI}
        title={`Task #${selectedTaskId}`}
        fetchPopupData={(properties: Record<string, any>) => {
          dispatch(setProjectState({ selectedTaskId: properties.id }));
        }}
        hideButton={taskStatusObj?.[selectedTaskId] !== 'UNLOCKED_TO_MAP'}
        buttonText="Lock Task"
        handleBtnClick={() => handleTaskLockClick()}
      />
      <BaseLayerSwitcher />
    </MapContainer>
  );
}
