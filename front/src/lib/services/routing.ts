/**
 * OSRM Routing Service for road-snapping GPS coordinates
 */

interface OSRMMatchResponse {
  code: string;
  matchings: Array<{
    geometry: {
      coordinates: [number, number][];
      type: string;
    };
    confidence: number;
    legs: Array<{
      summary: string;
      weight: number;
      duration: number;
      distance: number;
    }>;
  }>;
  tracepoints: Array<{
    name: string;
    location: [number, number];
    waypoint_index: number;
    matchings_index: number;
  } | null>;
}

interface SnapToRoadsResult {
  snappedCoordinates: [number, number][];
  confidence: number;
  success: boolean;
}

// Cache for road-snapped routes
const routeCache = new Map<string, SnapToRoadsResult>();

/**
 * Snap GPS coordinates to roads using OSRM Match API
 */
export async function snapToRoads(
  coordinates: [number, number][]
): Promise<SnapToRoadsResult> {
  if (coordinates.length < 2) {
    return {
      snappedCoordinates: coordinates,
      confidence: 0,
      success: false
    };
  }

  // Create cache key from coordinates
  const cacheKey = coordinates.map(c => `${c[0].toFixed(5)},${c[1].toFixed(5)}`).join('|');

  // Check cache
  const cached = routeCache.get(cacheKey);
  if (cached) {
    return cached;
  }

  try {
    // Format coordinates for OSRM (lng,lat format)
    const coordString = coordinates
      .map(([lat, lng]) => `${lng},${lat}`)
      .join(';');

    // Call OSRM Match API
    const url = `https://router.project-osrm.org/match/v1/driving/${coordString}?overview=full&geometries=geojson&radiuses=${coordinates.map(() => '50').join(';')}`;

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`OSRM API error: ${response.status}`);
    }

    const data: OSRMMatchResponse = await response.json();

    if (data.code !== 'Ok' || !data.matchings || data.matchings.length === 0) {
      // Return original coordinates if matching fails
      const result: SnapToRoadsResult = {
        snappedCoordinates: coordinates,
        confidence: 0,
        success: false
      };
      return result;
    }

    // Extract snapped coordinates (convert from [lng, lat] to [lat, lng])
    const snappedCoordinates = data.matchings[0].geometry.coordinates.map(
      ([lng, lat]) => [lat, lng] as [number, number]
    );

    const result: SnapToRoadsResult = {
      snappedCoordinates,
      confidence: data.matchings[0].confidence,
      success: true
    };

    // Cache result
    routeCache.set(cacheKey, result);

    return result;
  } catch (error) {
    console.error('OSRM snap to roads error:', error);
    // Return original coordinates on error
    return {
      snappedCoordinates: coordinates,
      confidence: 0,
      success: false
    };
  }
}

/**
 * Get route between two points using OSRM Route API
 */
export async function getRoute(
  start: [number, number],
  end: [number, number]
): Promise<[number, number][]> {
  try {
    const url = `https://router.project-osrm.org/route/v1/driving/${start[1]},${start[0]};${end[1]},${end[0]}?overview=full&geometries=geojson`;

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`OSRM Route API error: ${response.status}`);
    }

    const data = await response.json();

    if (data.code !== 'Ok' || !data.routes || data.routes.length === 0) {
      return [start, end];
    }

    // Convert from [lng, lat] to [lat, lng]
    return data.routes[0].geometry.coordinates.map(
      ([lng, lat]: [number, number]) => [lat, lng] as [number, number]
    );
  } catch (error) {
    console.error('OSRM route error:', error);
    return [start, end];
  }
}

/**
 * Clear the route cache
 */
export function clearRouteCache(): void {
  routeCache.clear();
}
