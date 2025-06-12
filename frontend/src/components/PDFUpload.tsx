'use client';

import React, { useState, useRef } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/Button';
import { useApp } from '@/contexts/AppContext';
import { apiService } from '@/services/api';

export default function PDFUpload() {
  const { sessionId, addAnalysis } = useApp();
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [uploadMessage, setUploadMessage] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.type === 'application/pdf') {
        setSelectedFile(file);
        setUploadStatus('idle');
        setUploadMessage('');
      } else {
        setUploadStatus('error');
        setUploadMessage('Por favor, selecione apenas arquivos PDF');
        setSelectedFile(null);
      }
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !sessionId) return;

    setIsUploading(true);
    setUploadStatus('idle');
    setUploadMessage('');

    try {
      const result = await apiService.uploadPDF(selectedFile, sessionId);
      
      if (result.error) {
        setUploadStatus('error');
        let errorMessage = result.error;
        
        // Add suggestion if available
        if (result.suggestion) {
          errorMessage += `\n\nSugestão: ${result.suggestion}`;
        }
        
        // Add debug info for development
        if (result.debug_info && process.env.NODE_ENV === 'development') {
          console.error('PDF Analysis Error:', result.debug_info);
        }
        
        setUploadMessage(errorMessage);
      } else {
        addAnalysis(result);
        setUploadStatus('success');
        setUploadMessage(
          result.cached 
            ? `Análise carregada do cache: ${result.fund_info.ticker}` 
            : `Análise concluída: ${result.fund_info.ticker}`
        );
        setSelectedFile(null);
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      }
    } catch (error) {
      setUploadStatus('error');
      setUploadMessage(error instanceof Error ? error.message : 'Erro ao processar PDF');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setUploadStatus('idle');
      setUploadMessage('');
    } else {
      setUploadStatus('error');
      setUploadMessage('Por favor, solte apenas arquivos PDF');
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-6 bg-gray-800 rounded-lg border border-gray-600">
      <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
        <FileText className="w-5 h-5" />
        Upload de Relatório FII
      </h2>

      {/* Drag and Drop Area */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors
          ${selectedFile 
            ? 'border-green-400 bg-green-400/10' 
            : 'border-gray-500 hover:border-gray-400 bg-gray-700/50'
          }`}
      >
        <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-300 mb-2">
          {selectedFile 
            ? `Arquivo selecionado: ${selectedFile.name}`
            : 'Arraste um arquivo PDF aqui ou clique para selecionar'
          }
        </p>
        <p className="text-sm text-gray-500 mb-4">
          {selectedFile 
            ? `Tamanho: ${(selectedFile.size / 1024 / 1024).toFixed(2)} MB`
            : 'Apenas arquivos PDF de relatórios de FII são aceitos (máx. 50MB)'
          }
        </p>
        
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileSelect}
          className="hidden"
        />
        
        <Button
          onClick={() => fileInputRef.current?.click()}
          variant="outline"
          className="mb-4"
        >
          Selecionar Arquivo
        </Button>
      </div>

      {/* Upload Button */}
      {selectedFile && (
        <div className="mt-4 flex justify-center">
          <Button
            onClick={handleUpload}
            disabled={isUploading}
            className="w-full max-w-xs"
          >
            {isUploading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Analisando...
              </>
            ) : (
              'Analisar PDF'
            )}
          </Button>
        </div>
      )}

      {/* Status Messages */}
      {uploadMessage && (
        <div className={`mt-4 p-4 rounded-lg border
          ${uploadStatus === 'success' 
            ? 'bg-green-400/20 text-green-300 border-green-400/30' 
            : 'bg-red-400/20 text-red-300 border-red-400/30'
          }`}
        >
          <div className="flex items-start gap-2">
            {uploadStatus === 'success' ? (
              <CheckCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
            ) : (
              <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
            )}
            <div className="text-sm whitespace-pre-line">{uploadMessage}</div>
          </div>
        </div>
      )}

      {/* Session Info */}
      <div className="mt-4 text-xs text-gray-500 text-center">
        Sessão: {sessionId?.slice(-8)}
      </div>
    </div>
  );
}