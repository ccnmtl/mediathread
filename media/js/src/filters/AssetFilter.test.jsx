/* eslint-env jest, node */
import fs from 'fs';
import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';
import AssetFilter from './AssetFilter';

it('renders the asset filter', async() => {
    const assetData = fs.readFileSync('media/js/test/asset-fixture.json');
    const fakeAssets = [JSON.parse(assetData)];

    // Use the asynchronous version of act to apply resolved promises
    const {getByText} = render(
        <AssetFilter
            assets={fakeAssets}
            tags={[]}
            terms={[]}
            viewMode="grid"
            hidePagination={false}
            currentPage={1}
            onUpdateItems={function() {}}
            onUpdateFilter={function() {}}
            setViewMode={function() {}}
            onClearFilter={function() {}}
            updatePageCount={function() {}}
        />
    );

    expect(getByText('Search')).toBeInTheDocument();
});
