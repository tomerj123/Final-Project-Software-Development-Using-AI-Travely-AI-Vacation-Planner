import { Grid } from '@mui/material';
import { FC } from 'react';

export const MainPageLayout: FC<any> = ({ children }) => (
    <div style={{ display: 'flex' }}>
        {children[0]}
        <Grid container padding={2} spacing={1}>
            <Grid item xs={12} sm={12} md={12} lg={12}>
                {children[1]}
            </Grid>
            <Grid item xs={12} sm={12} md={12} lg={12}>
                {children[2]}
            </Grid>
            <Grid item xs={12} sm={12} md={12} lg={12}>
                {children[3]}
            </Grid>
        </Grid>
    </div>
);
