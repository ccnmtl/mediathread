/* eslint-env jest, node */
import fs from 'fs';
import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';
import CollectionTab from './CollectionTab';

beforeEach(() => {
    global.ResizeObserver = jest.fn().mockImplementation(() => ({
        observe: jest.fn(),
        unobserve: jest.fn(),
        disconnect: jest.fn(),
    }));
});

const fakeUser = {
    id: 12,
    name: 'Test User'
};
const assetData = fs.readFileSync('media/js/test/asset-fixture.json');
const fakeAsset = JSON.parse(assetData);

it('renders the collection tab grid layout', async() => {
    const {getByText, getAllByText} = render(
        <CollectionTab
            currentUser={fakeUser.id}
            onUpdateAssets={function() {}}
            assets={[fakeAsset]} />
    );

    expect(getByText(fakeAsset.title)).toBeInTheDocument();
    expect(getAllByText('Previous')[0]).toBeInTheDocument();
    expect(getAllByText('Next')[0]).toBeInTheDocument();
});

it('renders the collection tab list layout', async() => {
    const {getByText, getAllByTestId} = render(
        <CollectionTab
            currentUser={fakeUser.id}
            onUpdateAssets={function() {}}
            assets={[fakeAsset]} />
    );

    const button = getAllByTestId('viewtoggle-list')[0];
    expect(button).toBeInTheDocument();

    // TODO: Fix this call
    // fireEvent.click(button);

    expect(getByText(fakeAsset.title)).toBeInTheDocument();
});
