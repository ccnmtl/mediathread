/* eslint-env jest, node */
import fs from 'fs';
import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';
import GridAsset from './GridAsset';

beforeEach(() => {
    global.ResizeObserver = jest.fn().mockImplementation(() => ({
        observe: jest.fn(),
        unobserve: jest.fn(),
        disconnect: jest.fn(),
    }));
});

it('renders the asset', async() => {
    const fakeUser = {
        id: 12,
        name: 'Test User'
    };
    const assetData = fs.readFileSync('media/js/test/asset-fixture.json');
    const fakeAsset = JSON.parse(assetData);

    // Use the asynchronous version of act to apply resolved promises
    const {getByText} = render(
        <GridAsset
            currentUser={fakeUser.id}
            asset={fakeAsset}
            enterAssetDetailView={function() {}} />
    );

    expect(getByText(fakeAsset.title)).toBeInTheDocument();
});
