import React from 'react';
import { SunAnimation, TitleComponentContainer, TitleComponentHeading } from './Title.s';

export const TitleComponent = () => (
    <TitleComponentContainer>
        <TitleComponentHeading>Travely</TitleComponentHeading>
        <SunAnimation /> {/* Animated Sun */}
    </TitleComponentContainer>
);
