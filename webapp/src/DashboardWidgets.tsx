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
  rectSortingStrategy,
  useSortable
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { 
  PieChart, 
  CreditCard,
  Target,
  Banknote,
  Users,
  Settings,
  FileText
} from 'lucide-react';

import { useRef } from 'react';

const SortableItem = ({ id, name, icon: Icon, onClick }: any) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
  } = useSortable({ id });

  const pointerDownTime = useRef(0);

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
      onPointerDown={(e) => {
        pointerDownTime.current = Date.now();
        if (listeners?.onPointerDown) listeners.onPointerDown(e);
      }}
      onPointerUp={() => {
        if (Date.now() - pointerDownTime.current < 200) {
          onClick();
        }
      }}
      onClick={(e) => e.stopPropagation()}
      className="neo-elem active:cursor-grabbing p-4 flex flex-col items-center justify-center w-[100px] hover:shadow-lg transition-shadow bg-[var(--bg-color)]"
    >
      <Icon size={32} className="mb-2 text-[var(--primary-color)]" />
      <span className="text-xs font-bold opacity-80 whitespace-nowrap">{name}</span>
    </div>
  );
};

export function DashboardWidgets({ onWidgetClick }: { onWidgetClick: (id: string, name: string) => void }) {
  const [items, setItems] = useState([
    { id: '1', name: 'Statistika', icon: PieChart },
    { id: '2', name: 'Hisobot', icon: FileText },
    { id: '3', name: 'Maqsadlar', icon: Target },
    { id: '4', name: 'Kreditlar', icon: Banknote },
    { id: '5', name: 'Qarzlarim', icon: Users },
    { id: '6', name: 'Kartalar', icon: CreditCard },
    { id: '7', name: 'Sozlamalar', icon: Settings },
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
      <h2 className="text-lg font-bold mb-4 opacity-80">Menyu va Vidjetlar (Drag & Drop)</h2>
      <DndContext 
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext 
          items={items.map(i => i.id)}
          strategy={rectSortingStrategy}
        >
          <div className="flex flex-wrap gap-4 pb-4 px-1" style={{ touchAction: 'none' }}>
            {items.map((item) => (
              <SortableItem 
                key={item.id} 
                id={item.id} 
                name={item.name} 
                icon={item.icon} 
                onClick={() => onWidgetClick(item.id, item.name)}
              />
            ))}
          </div>
        </SortableContext>
      </DndContext>
    </div>
  );
}
