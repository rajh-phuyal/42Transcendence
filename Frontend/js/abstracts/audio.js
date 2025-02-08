export default class AudioPlayer {
    static instance = null;

    constructor() {
        if (AudioPlayer.instance) {
            return AudioPlayer.instance;
        }

        this.maxVolumeMusic = 0.5;
        this.maxVolumeSounds = 0.75;
        this.soundsEnabled = true;
        this.musicEnabled = true;
        this.currentSong = null;
        this.playing = false;
        this.songs = [
            { mapId: 0, audio: new Audio("../assets/audio/lobby.mp3") },
            { mapId: 1, audio: new Audio("../assets/audio/ufo.mp3") },
            { mapId: 2, audio: new Audio("../assets/audio/lizard-people.mp3") },
            { mapId: 3, audio: new Audio("../assets/audio/snowman.mp3") },
            { mapId: 4, audio: new Audio("../assets/audio/lochness.mp3") }
        ];

        this.sounds = [
            { name: "beep1", audio: new Audio("../assets/audio/beep1.mp3") },
            { name: "beep2", audio: new Audio("../assets/audio/beep2.mp3") },
            { name: "paddle", audio: new Audio("../assets/audio/paddle.mp3") },
            { name: "powerup", audio: new Audio("../assets/audio/powerup.mp3") },
            { name: "wall", audio: new Audio("../assets/audio/wall.mp3") },
            { name: "gameover", audio: new Audio("../assets/audio/gameover.mp3") },
            { name: "pause", audio: new Audio("../assets/audio/pause.mp3") },
            { name: "unpause", audio: new Audio("../assets/audio/unpause.mp3") },
            { name: "score", audio: new Audio("../assets/audio/score.mp3") },
            { name: "toggle", audio: new Audio("../assets/audio/toggle.mp3") }
        ];

        AudioPlayer.instance = this;
    }

    static getInstance() {
        if (!AudioPlayer.instance) {
            AudioPlayer.instance = new AudioPlayer();
        }
        return AudioPlayer.instance;
    }

    toggleMusic() {
        this.playSound("toggle");
        this.musicEnabled = !this.musicEnabled;
        if (!this.musicEnabled) {
            this.stop();
        } else {
            if (this.currentSong)
                this.play(this.currentSong.mapId);
        }
    }

    toggleSound() {
        this.soundsEnabled = !this.soundsEnabled;
        this.playSound("toggle");
    }

    setAudioPreferences({ music = this.musicEnabled, sounds = this.soundsEnabled }) {
        this.musicEnabled = music;
        this.soundsEnabled = sounds;

        if (!this.musicEnabled && this.currentSong) {
            this.stop();
        }
    }

    playSound(name) {
        if (!this.soundsEnabled) return;
        if (!name) return;
        if (name === "none") return;

        const sound = this.sounds.find(sound => sound.name === name);
        if (sound) {
            sound.audio.play();
        } else {
            console.error("Sound not found:", name);
        }
    }

    play(mapId) {
        if (!this.musicEnabled) return;
        const newSong = this.songs.find(song => song.mapId === mapId);
        if (!newSong) {
            console.error("Song not found:", mapId);
            return;
        }

        // Make sure the song is looped
        newSong.audio.loop = true;

        if (this.playing && this.currentSong === newSong) {
            console.log("Song is already playing:", newSong);
            return;
        }

        if (this.playing) {
            this.crossfade(this.currentSong, newSong);
        } else {
            this.playing = true;
            this.startFadeIn(newSong, 1000);
        }
    }

    crossfade(oldSong, newSong) {
        if (!this.musicEnabled) return;

        this.startFadeOut(oldSong, 1000, () => {
            oldSong.audio.pause();
            oldSong.audio.currentTime = 0;
            oldSong.audio.volume = this.maxVolumeMusic;
        });

        this.startFadeIn(newSong, 1000);
    }

    startFadeOut(song, duration, callback) {
        const interval = 100;
        const steps = duration / interval;
        let step = 0;

        const fadeOut = setInterval(() => {
            if (step >= steps) {
                clearInterval(fadeOut);
                if (callback) callback();
            } else {
                song.audio.volume = this.maxVolumeMusic - step / steps;
                step++;
            }
        }, interval);
    }

    startFadeIn(song, duration) {
        song.audio.volume = 0;
        song.audio.play();

        const interval = 100;
        const steps = duration / interval;
        let step = 0;

        const fadeIn = setInterval(() => {
            if (step >= steps) {
                clearInterval(fadeIn);
                song.audio.volume = this.maxVolumeMusic;
            } else {
                song.audio.volume = step / steps;
                step++;
            }
        }, interval);

        this.currentSong = song;
    }

    stop() {
        if (this.playing) {
            this.startFadeOut(this.currentSong, 1000, () => {
                this.currentSong.audio.pause();
                this.currentSong.audio.currentTime = 0;
                this.playing = false;
            });
        }
    }
}

// Create and export a single instance
const audioPlayer = AudioPlayer.getInstance();
export { audioPlayer };
