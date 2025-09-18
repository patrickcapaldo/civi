import React, { useRef, useEffect } from 'react';
import Latex from 'react-latex';

const LatexRenderer = ({ children, displayMode }) => {
    // We don't need a ref since `react-latex` handles this, but it's good practice
    // with other libraries like vanilla KaTeX
    return <Latex displayMode={displayMode}>{children}</Latex>;
};

export default React.memo(LatexRenderer);
