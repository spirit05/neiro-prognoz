# train_model.py
import json
from ml.core.trainer import EnhancedTrainer

# Загрузи данные
with open('/opt/dev/data/datasets/dataset.json') as f:
    groups = json.load(f)

# Обучи модель
trainer = EnhancedTrainer()
success = trainer.train(groups, epochs=50)

if success:
    print("✅ Модель успешно обучена и сохранена!")
else:
    print("❌ Ошибка обучения")
