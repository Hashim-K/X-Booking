'use client';

import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

interface TimeSelectorProps {
  selectedTimes: string[];
  onTimesChange: (times: string[]) => void;
}

interface SortableItemProps {
  id: string;
  index: number;
}

function SortableItem({ id, index }: SortableItemProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
  } = useSortable({ id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className="bg-gray-100 p-3 rounded-md flex items-center cursor-move"
    >
      <span className="mr-2">☰</span>
      {index + 1}. {id}
    </div>
  );
}

export default function TimeSelector({ selectedTimes, onTimesChange }: TimeSelectorProps) {
  const availableTimes = [
    "07:00", "08:00", "09:00", "10:00", "11:00", "12:00",
    "13:00", "14:00", "15:00", "16:00", "17:00", "18:00",
    "19:00", "20:00", "21:00", "22:00", "23:00"
  ];

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleTimeToggle = (time: string) => {
    if (selectedTimes.includes(time)) {
      onTimesChange(selectedTimes.filter(t => t !== time));
    } else {
      onTimesChange([...selectedTimes, time]);
    }
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      const oldIndex = selectedTimes.indexOf(active.id as string);
      const newIndex = selectedTimes.indexOf(over.id as string);

      onTimesChange(arrayMove(selectedTimes, oldIndex, newIndex));
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Select Times</h2>
        <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-2">
          {availableTimes.map((time) => (
            <label
              key={time}
              className="flex items-center space-x-2 cursor-pointer"
            >
              <input
                type="checkbox"
                checked={selectedTimes.includes(time)}
                onChange={() => handleTimeToggle(time)}
                className="rounded text-blue-500"
              />
              <span>{time}</span>
            </label>
          ))}
        </div>
      </div>

      {selectedTimes.length > 0 && (
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-3">
            Priority Order
          </h3>
          <DndContext
            sensors={sensors}
            collisionDetection={closestCenter}
            onDragEnd={handleDragEnd}
          >
            <SortableContext
              items={selectedTimes}
              strategy={verticalListSortingStrategy}
            >
              <div className="space-y-2">
                {selectedTimes.map((time, index) => (
                  <SortableItem key={time} id={time} index={index} />
                ))}
              </div>
            </SortableContext>
          </DndContext>
        </div>
      )}
    </div>
  );
} 