import React, { useEffect, useRef } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";

mapboxgl.accessToken =
  "pk.eyJ1IjoiZXJpY25pbmciLCJhIjoiY21icXlubWM1MDRiczJvb2xwM2p0amNyayJ9.n-3O6JI5nOp_Lw96ZO5vJQ";

export default function CoverageMap({
  coords,
  coverageZones,
  onMapLoad,
}) {
  const mapRef = useRef(null);
  const mapObj = useRef(null);
  const markersRef = useRef([]);

  useEffect(() => {
    if (mapObj.current || !mapRef.current) return;

    try {
      mapObj.current = new mapboxgl.Map({
        container: mapRef.current,
        style: "mapbox://styles/mapbox/streets-v12",
        center: coords,
        zoom: 12,
        attributionControl: false,
      });
    } catch (error) {
      console.error("Error initializing map:", error);
      return;
    }

    mapObj.current.on("load", () => {
      // Add Internet Air (AIA) coverage zones (green, larger radius)
      coverageZones.internetAir.forEach((zone, idx) => {
        const sourceId = `aia-coverage-${idx}`;
        const layerId = `aia-coverage-layer-${idx}`;

        // Create circle polygon
        const radiusDegrees = zone.radius;
        const points = 64;
        const coordinates = [];
        for (let i = 0; i < points; i++) {
          const angle = (i / points) * 2 * Math.PI;
          const lng = zone.center[0] + radiusDegrees * Math.cos(angle);
          const lat = zone.center[1] + radiusDegrees * Math.sin(angle);
          coordinates.push([lng, lat]);
        }
        coordinates.push(coordinates[0]); // Close the polygon

        mapObj.current.addSource(sourceId, {
          type: "geojson",
          data: {
            type: "Feature",
            geometry: {
              type: "Polygon",
              coordinates: [coordinates],
            },
          },
        });

        mapObj.current.addLayer({
          id: layerId,
          type: "fill",
          source: sourceId,
          paint: {
            "fill-color": "#10b981", // green-500
            "fill-opacity": 0.25,
          },
        });

        // Add border
        mapObj.current.addLayer({
          id: `${layerId}-outline`,
          type: "line",
          source: sourceId,
          paint: {
            "line-color": "#059669", // green-600
            "line-width": 2,
            "line-opacity": 0.5,
          },
        });
      });

      // Add Fiber coverage zones (blue, smaller radius, on top)
      coverageZones.fiber.forEach((zone, idx) => {
        const sourceId = `fiber-coverage-${idx}`;
        const layerId = `fiber-coverage-layer-${idx}`;

        // Create circle polygon
        const radiusDegrees = zone.radius;
        const points = 64;
        const coordinates = [];
        for (let i = 0; i < points; i++) {
          const angle = (i / points) * 2 * Math.PI;
          const lng = zone.center[0] + radiusDegrees * Math.cos(angle);
          const lat = zone.center[1] + radiusDegrees * Math.sin(angle);
          coordinates.push([lng, lat]);
        }
        coordinates.push(coordinates[0]);

        mapObj.current.addSource(sourceId, {
          type: "geojson",
          data: {
            type: "Feature",
            geometry: {
              type: "Polygon",
              coordinates: [coordinates],
            },
          },
        });

        mapObj.current.addLayer({
          id: layerId,
          type: "fill",
          source: sourceId,
          paint: {
            "fill-color": "#3b82f6", // blue-500
            "fill-opacity": 0.3,
          },
        });

        // Add border
        mapObj.current.addLayer({
          id: `${layerId}-outline`,
          type: "line",
          source: sourceId,
          paint: {
            "line-color": "#2563eb", // blue-600
            "line-width": 2,
            "line-opacity": 0.6,
          },
        });
      });

      // Add house marker at customer location
      const el = document.createElement("div");
      el.className = "house-marker";
      el.innerHTML = `
        <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="20" cy="20" r="18" fill="white" stroke="#7c3aed" stroke-width="3"/>
          <path d="M20 10L28 17H26V26H22V21H18V26H14V17H12L20 10Z" fill="#7c3aed"/>
        </svg>
      `;
      el.style.cursor = "pointer";

      const marker = new mapboxgl.Marker({
        element: el,
        anchor: "center",
      })
        .setLngLat(coords)
        .addTo(mapObj.current);

      markersRef.current.push(marker);

      if (onMapLoad && typeof onMapLoad === 'function') {
        try {
          onMapLoad(mapObj.current);
        } catch (error) {
          console.error("Error in onMapLoad callback:", error);
        }
      }
    });

    // Handle window resize
    const handleResize = () => {
      if (mapObj.current) {
        mapObj.current.resize();
      }
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      markersRef.current.forEach((m) => m.remove());
      if (mapObj.current) {
        mapObj.current.remove();
        mapObj.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run once on mount

  return (
    <div className="relative w-full h-full">
      <div ref={mapRef} className="absolute inset-0 w-full h-full" />
      
      {/* Legend */}
      <div className="absolute top-4 left-4 bg-white rounded-lg shadow-lg p-4 z-20">
        <h3 className="font-semibold text-sm text-gray-900 mb-3">Coverage Map</h3>
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-blue-500 opacity-50 rounded"></div>
            <span className="text-sm text-gray-700">AT&T Fiber</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-green-500 opacity-50 rounded"></div>
            <span className="text-sm text-gray-700">Internet Air</span>
          </div>
          <div className="flex items-center space-x-2">
            <svg width="16" height="16" viewBox="0 0 16 16">
              <circle cx="8" cy="8" r="7" fill="white" stroke="#7c3aed" strokeWidth="2"/>
            </svg>
            <span className="text-sm text-gray-700">Your location</span>
          </div>
        </div>
      </div>

      <style>{`
        .house-marker {
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
        }
      `}</style>
    </div>
  );
}
