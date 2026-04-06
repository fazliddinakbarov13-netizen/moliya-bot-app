import { useState } from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  horizontalListSortingStrategy,
  useSortable
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { PieChart, Activity, CreditCard } from 'lucide-react';

const SortableItem = ({ id, name, icon: Icon }: any) => {
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
      className="neo-elem cursor-grab active:cursor-grabbing p-4 flex flex-col items-center justify-center min-w-[100px] hover:shadow-lg transition-shadow bg-[var(--bg-color)]"
    >
      <Icon size={32} className="mb-2 text-[var(--primary-color)]" />
      <span className="text-xs font-bold opacity-80">{name}</span>
    </div>
  );
};

export function DashboardWidgets() {
  const [items, setItems] = useState([
    { id: '1', name: 'Statistika', icon: PieChart },
    { id: '2', name: 'Faollik', icon: Activity },
    { id: '3', name: 'Kartalar', icon: CreditCard },
  ]);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const handleDragEnd = (event: any) => {
    const { active, over } = event;
    
    if (active.id !== over.id) {
      setItems((items) => {
        const oldIndex = items.findIndex(item => item.id === active.id);
        const newIndex = items.findIndex(item => item.id === over.id);
        return arrayMove(items, oldIndex, newIndex);
      });
    }
  };

  return (
    <div className="w-full mt-6 mb-8">
      <h2 className="text-lg font-bold mb-4 opacity-80">Vidjetlar (Drag & Drop)</h2>
      <DndContext 
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext 
          items={items.map(i => i.id)}
          strategy={horizontalListSortingStrategy}
        >
          <div className="flex gap-4 overflow-x-auto pb-4 px-1" style={{ touchAction: 'none' }}>
            {items.map((item) => (
              <SortableItem key={item.id} id={item.id} name={item.name} icon={item.icon} />
            ))}
          </div>
        </SortableContext>
      </DndContext>
    </div>
  );
}
