
import React from 'react';
import { Box, Chip, Typography } from '@mui/material';

const ActiveFilters = ({ filters, onRemoveFilter }) => {
    const activeFilters = [];

    if (filters.search) {
        activeFilters.push({ type: 'search', value: filters.search, label: `Title Keyword(s): "${filters.search}"` });
    }
    filters.countries.forEach(c => activeFilters.push({ type: 'countries', value: c, label: `Country: ${c}` }));
    filters.industries.forEach(i => activeFilters.push({ type: 'industries', value: i, label: `Industry: ${i}` }));
    filters.pillars.forEach(p => activeFilters.push({ type: 'pillars', value: p, label: `Pillar: ${p}` }));

    if (activeFilters.length === 0) {
        return null;
    }

    return (
        <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 1, alignItems: 'center' }}>
            <Typography variant="subtitle2">Active Filters:</Typography>
            {activeFilters.map(filter => (
                <Chip 
                    key={filter.label}
                    label={filter.label}
                    onDelete={() => onRemoveFilter(filter.type, filter.value)}
                />
            ))}
        </Box>
    );
};

export default ActiveFilters;
