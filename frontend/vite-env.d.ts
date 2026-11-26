/// <reference types="vite/client" />
/// <reference types="vite-plugin-svgr/client" />

interface ImportMetaEnv {
  /**
   * Approved build-time entry-point selection. Set to "live" only when building
   * a packaged local-engine client; hosted preview/production builds must leave
   * this unset so they always serve the synthetic preview (`App`).
   */
  readonly VITE_ENGINE?: "live";
}

declare module '*.svg?react' {
  import * as React from 'react';
  export const ReactComponent: React.FunctionComponent<React.SVGProps<SVGSVGElement>>;
  const src: string;
  export default src;
}

declare module '*.svg?import&react' {
  import * as React from 'react';
  export const ReactComponent: React.FunctionComponent<React.SVGProps<SVGSVGElement>>;
  const src: string;
  export default src;
}
