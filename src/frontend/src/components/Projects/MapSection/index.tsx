import { useMapLibreGLMap } from '@Components/common/MapLibreComponents';
import MapContainer from '@Components/common/MapLibreComponents/MapContainer';
import BaseLayerSwitcher from '@Components/common/MapLibreComponents/BaseLayerSwitcher';
import { useGetProjectsListQuery } from '@Api/projects';
import centroid from '@turf/centroid';
import VectorLayerWithCluster from './VectorLayerWithCluster';

export default function ProjectsMapSection() {
  const { map, isMapLoaded } = useMapLibreGLMap({
    containerId: 'dashboard-map',
    mapOptions: {
      zoom: 5,
      center: [84.124, 28.3949],
      maxZoom: 19,
    },
    disableRotation: true,
  });
  const { data: projectsList, isLoading } = useGetProjectsListQuery({
    select: (data: any) => {
      // find all polygons centroid and set to geojson save to single geojson
      const combinedGeojson = data?.data?.reduce(
        (acc: Record<string, any>, current: Record<string, any>) => {
          return {
            ...acc,
            features: [...acc.features, centroid(current.outline)],
          };
        },
        {
          type: 'FeatureCollection',
          features: [],
        },
      );
      return combinedGeojson;
    },
  });

  // useEffect(() => {
  //   if (!projectsList) return;
  //   const bbox = getBbox(projectsList as FeatureCollection);
  //   map?.fitBounds(bbox as LngLatBoundsLike, { padding: 30 });
  // }, [projectsList, map]);

  return (
    <MapContainer
      map={map}
      isMapLoaded={isMapLoaded}
      containerId="dashboard-map"
      style={{
        width: '55%',
        height: '36.375rem',
      }}
    >
      <VectorLayerWithCluster
        map={map}
        visibleOnMap={!isLoading}
        mapLoaded={isMapLoaded}
        sourceId="clustered-projects"
        geojson={projectsList}
      />

      {/* <VectorLayer
        map={map as Map}
        isMapLoaded={isMapLoaded}
        id="uploaded-project-area"
        geojson={projectsList as GeojsonType}
        visibleOnMap={true}
        layerOptions={{
          type: 'fill',
          paint: {
            'fill-color': '#328ffd',
            'fill-outline-color': '#000000',
            'fill-opacity': 0.8,
          },
        }}
      /> */}

      <BaseLayerSwitcher />
    </MapContainer>
  );
}
