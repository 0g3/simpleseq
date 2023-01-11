import simpleseq 

# トラックの作成
sin_t1 = simpleseq.Track(simpleseq.wave_sin)
sin_t2 = simpleseq.Track(simpleseq.wave_sin)
sin_t3 = simpleseq.Track(simpleseq.wave_sin)

# 打ち込み
sin_t1.add(simpleseq.Note("C3", 480))
sin_t2.add(simpleseq.Note("E3", 480))
sin_t3.add(simpleseq.Note("G3", 480))

sin_t1.add(simpleseq.Note("C3", 480))
sin_t2.add(simpleseq.Note("E3", 480))
sin_t3.add(simpleseq.Note("G#3", 480))

sin_t1.add(simpleseq.Note("C3", 480))
sin_t2.add(simpleseq.Note("E3", 480))
sin_t3.add(simpleseq.Note("A3", 480))

sin_t1.add(simpleseq.Note("C3", 480))
sin_t2.add(simpleseq.Note("E3", 480))
sin_t3.add(simpleseq.Note("A#3", 480))

# 再生
seq = simpleseq.Sequencer([sin_t1, sin_t2, sin_t3], 120)
seq.play()
