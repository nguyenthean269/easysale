import { UrlMatchResult, UrlSegment } from '@angular/router';

/**
 * Creates a route matcher function for apartment listing routes
 * @param routePath The base route path (e.g., 'can-ho-chung-cu-ban')
 * @returns A matcher function that matches routes starting with the given path
 */
export function createApartmentListingMatcher(routePath: string) {
  return (segments: UrlSegment[]): UrlMatchResult | null => {
    if (segments.length === 0) {
      return null;
    }
    
    const firstSegment = segments[0].path;
    
    // Match if segment starts with the route path
    if (firstSegment.startsWith(routePath)) {
      return { consumed: segments };
    }
    
    return null;
  };
}




