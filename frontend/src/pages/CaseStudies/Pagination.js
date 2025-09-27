
import React from 'react';
import { Box, Pagination as MuiPagination } from '@mui/material';

const Pagination = ({ totalPages, page, onPageChange }) => {
    if (totalPages <= 1) {
        return null;
    }

    const handleChange = (event, value) => {
        onPageChange(value);
    };

    return (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4, mb: 4 }}>
            <MuiPagination 
                count={totalPages}
                page={page}
                onChange={handleChange}
                color="primary"
            />
        </Box>
    );
};

export default Pagination;
