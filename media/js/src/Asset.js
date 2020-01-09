export default class Asset {
    constructor(data) {
        this.asset = data;
    }
    /**
     * Get asset type.
     *
     * This corresponds to Asset.primary_labels in
     * mediathread/assetmgr/models.py
     */
    getType() {
        let assetType = this.asset.primary_type;
        if (assetType === 'youtube' || assetType === 'mp4_pseudo') {
            assetType = 'video';
        } else if (assetType === 'image_fpxid') {
            assetType = 'image';
        }
        return assetType;
    }
    getThumbnail() {
        if (!this.asset) {
            return null;
        }

        return this.asset.thumb_url ||
            (
                (this.asset.sources &&
                 this.asset.sources.image) ?
                    this.asset.sources.image.url : null
            );

    }
    getImage() {
        if (!this.asset || !this.asset.sources) {
            return null;
        }

        return this.asset.sources.image ||
            this.asset.sources.thumb;
    }
}
