import getYouTubeID from 'get-youtube-id';
import {getAssetType} from './utils';

export default class Asset {
    constructor(data) {
        this.asset = data;
    }
    getType() {
        return getAssetType(this.asset.primary_type);
    }
    getThumbnail() {
        if (!this.asset) {
            return null;
        }

        // Use youtube's thumbnail format for getting the biggest
        // thumbnail available.
        if (
            this.asset.primary_type === 'youtube' &&
                this.asset.sources &&
                this.asset.sources.url
        ) {
            const youtubeId = getYouTubeID(this.asset.sources.url.url);
            return `https://img.youtube.com/vi/${youtubeId}/hqdefault.jpg`;
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
    getVideo() {
        if (!this.asset || !this.asset.sources) {
            return null;
        }

        let source = null;

        if (this.asset.primary_type === 'mp4_pseudo') {
            source = this.asset.sources.mp4_pseudo.url;
        } else {
            source = this.asset.sources.url.url ||
                this.asset.sources.youtube.url;
        }

        return source;
    }
}
