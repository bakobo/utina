# utina.replay cannot export a record holding an evaluation seal: seal_evaluation emits {t: evl} with no 'i', and replay's export reads event.body['i'] for every event (KeyError). Adding evl to replay.KINDS (#12) is necessary but not sufficient; Meridian's record still cannot cross utina.replay.
kind: todo
created: 2026-10-01T14:08Z

