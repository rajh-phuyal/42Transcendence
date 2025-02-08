export default class AudioPlayer {
    // Static property to store songs
    static songs = [
        { mapId: 0, audio: new Audio("../assets/audio/lobby.mp3") },
        { mapId: 1, audio: new Audio("../assets/audio/ufo.mp3") },
        { mapId: 2, audio: new Audio("../assets/audio/lizard-people.mp3") },
        { mapId: 3, audio: new Audio("../assets/audio/snowman.mp3") },
        { mapId: 4, audio: new Audio("../assets/audio/lochness.mp3") }
    ];

    static sounds = [
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

    static currentSong = null; // Track the currently playing song

    static playSound(name) {
        const sound = this.sounds.find(sound => sound.name === name);
        if (sound)
            sound.audio.play();
        else
            console.error('Sound not found:', name);
    }

    // Static method to play a song
    static play(mapId) {
        console.log('Starting:', mapId);
        const newSong = this.songs.find(song => song.mapId === mapId);
        if (!newSong) {
            console.error('Song not found:', mapId);
            return;
        }

        // Dont restart the song if it is already playing
        if (this.currentSong === newSong) {
            console.log('Song is already playing:', newSong);
            return;
        }

        // Crossfade to the new song (if there is one currently playing)
        if (this.currentSong) {
            this.crossfade(this.currentSong, newSong);
        } else {
            // No song currently playing, start immediately
            newSong.audio.volume = 1; // Ensure full volume
            newSong.audio.play();
            this.currentSong = newSong;
        }
    }

    static crossfade(oldSong, newSong) {
        const fadeOutDuration = 1000; // 1 seconds
        const fadeInDuration = 1000; // 1 seconds
        const interval = 100; // How often to update volume (ms)
        const steps = fadeOutDuration / interval;

        let step = 0;
        this.startFadeIn(newSong, fadeInDuration);
        const fadeOut = setInterval(() => {
            if (step >= steps) {
                clearInterval(fadeOut);
                oldSong.audio.pause(); // Stop old song
                oldSong.audio.currentTime = 0; // Reset position
                oldSong.audio.volume = 1; // Reset volume for future plays

            } else {
                oldSong.audio.volume = 1 - (step / steps);
                step++;
            }
        }, interval);
    }

    static startFadeIn(newSong, duration) {
        newSong.audio.volume = 0;
        newSong.audio.play();

        const interval = 100; // How often to update volume (ms)
        const steps = duration / interval;

        let step = 0;

        const fadeIn = setInterval(() => {
            if (step >= steps) {
                clearInterval(fadeIn);
                newSong.audio.volume = 1; // Ensure full volume
            } else {
                newSong.audio.volume = step / steps;
                step++;
            }
        }, interval);

        this.currentSong = newSong;
    }

    // Static method to stop playing
    static stop() {
        if (this.currentSong) {
            this.currentSong.audio.pause();
            this.currentSong.audio.currentTime = 0; // Reset audio to start
            this.currentSong = null; // Clear reference
        }
    }
}